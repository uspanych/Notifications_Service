from .base import BaseNotifications, RabbitMQ, RedisCache

from redis.asyncio import Redis
from functools import lru_cache
from fastapi import Depends

from adapters.rabbit import get_rabbit, RMQ
from models.notifications import NewSeriesModel, Series, VerifyUserModel, LikeModel
from sqlalchemy.ext.asyncio import AsyncSession
from adapters.redis import get_redis
import uuid
from .scheduler.scheduler import get_scheduler
from .scheduler.task import create_event_like


class FastNotificationsService(BaseNotifications):
    async def _insert_data_db(
        self,
        new_series: NewSeriesModel,
        session: AsyncSession,
    ) -> None:
        """Метод сохраняет новую серию в БД.

        Args:
            new_series (NewSeriesModel): Модель данных серии.
            session (AsyncSession): Активная сессия с БД.


        """

        await self.insert_data_in_db(
            model=Series(
                id=uuid.uuid4(),
                movie_id=new_series.movie_id,
                movie_name=new_series.movie_name,
                series_number=new_series.series_number,
                user_id=new_series.user_id,
                user_name=new_series.user_name,
                user_email=new_series.user_email,
            ),
            session=session,
        )

    async def check_new_series(
        self,
        new_series: NewSeriesModel,
        session: AsyncSession,
    ) -> None:
        """Метод выполняет проверку уведомления.

        Уведомление проверяется на наличие в базе,
        ключом поиска выступает movie_id. В случае, если
        данное уведомление отсутствует в базе, то
        создается новая запись в таблице и отправляется в очередь.

        Args:
            new_series (NewSeriesModel): Модель данных.
            session (AsyncSession): Активное соединение с БД.


        """

        old_series = await self.select_id_data_db(
            model=Series,
            session=session,
            item_id=new_series.movie_id
        )
        if old_series is None:

            await self.set_data_in_queue(
                data=new_series.dict() | {'task_id': 2},
                routing_key='event.series',
                correlation_id=new_series.movie_id
            )

            await self._insert_data_db(
                session=session,
                new_series=new_series,
            )

        else:

            if old_series.series_number < new_series.series_number:

                await self.set_data_in_queue(
                    data=new_series.dict() | {'task_id': 2},
                    routing_key='event.series',
                    correlation_id=new_series.movie_id
                )

                await self.update_data_in_db(
                    model=Series,
                    session=session,
                    key='series_number',
                    value=new_series.series_number,
                )

    async def verify_email(
        self,
        new_verify: VerifyUserModel,
    ) -> None:
        """Метод отправляет уведомление о подтверждении регистрации.

        Args:
            new_verify (VerifyUser): Модель данных.


        """

        await self.set_data_in_queue(
            data=new_verify.dict() | {'task_id': 3},
            routing_key='event.verify',
            correlation_id=new_verify.user_id,
        )

    async def like_event(
        self,
        new_like: LikeModel,
    ) -> None:

        scheduler = await get_scheduler()
        data = await self.cache_handler.get_by_id(key=new_like.subject_id)

        if data is None:
            # scheduler.add_job(create_event_like, 'interval', minutes=10, args=(new_like,))
            scheduler.add_job(create_event_like, 'interval', seconds=1, args=(new_like,), id=new_like.subject_id)
            await self.cache_handler.set_by_id(
                key=new_like.subject_id,
                value=1,
                ttl=30
            )

        else:
            old_value = await self.cache_handler.get_by_id(
                key=new_like.subject_id,
            )

            await self.set_data_by_id(
                key=new_like.subject_id,
                value=str(int(old_value) + 1),
            )
        

@lru_cache()
def get_notifications_service(
    rabbit: RMQ = Depends(get_rabbit),
    redis: Redis = Depends(get_redis)
) -> FastNotificationsService:
    return FastNotificationsService(RabbitMQ(rabbit), RedisCache(redis))
