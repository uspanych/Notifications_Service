import abc
import json
from typing import Any, Callable, Optional

import sqlalchemy.exc
from redis.asyncio import Redis
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import SQLModel

from adapters.rabbit import RMQ


class AbstractQueue(abc.ABC):
    @abc.abstractmethod
    async def send_data(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    async def read_data(self, *args, **kwargs):
        raise NotImplementedError


class AbstractCache(abc.ABC):
    @abc.abstractmethod
    async def get_by_id(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    async def set_by_id(self, *args, **kwargs):
        raise NotImplementedError


class AbstractSender(abc.ABC):
    @abc.abstractmethod
    async def send_message(self, *args, **kwargs):
        raise NotImplementedError


class PushSender(AbstractSender):
    def __init__(
        self,
        service_url: str
    ):
        self.service_url = service_url

    async def send_message(self, *args, **kwargs):
        pass


class SMSSender(AbstractSender):
    def __int__(
        self,
        service_url: str
    ):
        self.service_url = service_url

    async def send_message(self, *args, **kwargs):
        pass


class RedisCache(AbstractCache):
    def __init__(
        self,
        redis: Redis
    ):
        self.redis = redis

    async def get_by_id(self, *args, **kwargs):
        data = await self.redis.get(kwargs.get('key'))
        if not data:
            return None

        return json.loads(data)

    async def set_by_id(self, *args, **kwargs):
        await self.redis.set(
            kwargs.get('key'),
            kwargs.get('value'),
            kwargs.get('ttl'),
        )


class RabbitMQ(AbstractQueue):
    def __init__(
        self,
        rabbit: RMQ,
    ):
        self.rabbit = rabbit

    async def send_data(self, *args, **kwargs):
        await self.rabbit.send(
            routing_key=kwargs.get('routing_key'),
            data=kwargs.get('data'),
            correlation_id=kwargs.get('correlation_id')
        )

    async def read_data(self, *args, **kwargs):
        await self.rabbit.consume_queue(
            func=kwargs.get('func'),
            binding_keys=kwargs.get('binding_keys'),
            queue_name=kwargs.get('queue_name'),
        )


class BaseNotifications:
    """Базовый класс для работы с хранилищем и очередью."""

    def __init__(
        self,
        queue_handler: AbstractQueue,
        cache_handler: AbstractCache,
    ):
        self.queue_handler = queue_handler
        self.cache_handler = cache_handler
        self.FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5

    async def set_data_in_queue(
        self,
        data: dict,
        routing_key: str,
        correlation_id: str,
    ) -> None:
        """Метод сохраняет данные в очередь по-нужному routing_key.

        Args:
            data (dict): Полезная нагрузка.
            routing_key (str): Ключ маршрутизации.
            correlation_id (str): id сообщения.


        """

        await self.queue_handler.send_data(
            data=data,
            routing_key=routing_key,
            correlation_id=correlation_id,
        )

    async def read_data_queue(
        self,
        func: Callable,
        binding_keys: str | list[str],
        queue_name: str,
    ) -> None:
        """Метод читает данные из очереди.

        Args:
            func (Callable): Функция - логика над данными.
            binding_keys (str): Ключ привязки.
            queue_name (str): Название очереди.


        """

        await self.queue_handler.read_data(
            func=func,
            binding_keys=binding_keys,
            queue_name=queue_name,
        )

    @staticmethod
    async def select_all_data_db(
        model: SQLModel,
        session: AsyncSession,
    ) -> Optional[list]:
        """Метод возвращает данные из БД.

        Args:
            model (SQLModel): Модель данных.
            session (AsyncSession): Активная сессия с БД.

        Returns:
             SQLModel: Модель данных.


        """

        some_data = await session.execute(select(model))
        result = some_data.scalars().all()
        return result

    @staticmethod
    async def select_id_data_db(
        model: SQLModel,
        session: AsyncSession,
        item_id: str,
    ) -> Optional[SQLModel]:
        """Метод получает данные из БД по id.

        Args:
            model (SQLModel): Модель данных.
            session (AsyncSession): Активная сессия с БД.
            item_id: (UUID): id записи с таблице.


        Returns:
            SQLModel


        """
        try:
            result = await session.execute(select(model).filter_by(movie_id=item_id))
            return result.scalar_one()

        except sqlalchemy.exc.NoResultFound:
            return None

    @staticmethod
    async def insert_data_in_db(
        model: SQLModel | list[SQLModel],
        session: AsyncSession,
    ) -> None:
        """Метод сохраняет данные в БД.

        Args:
            model (SQLModel): Модель данных.
            session (AsyncSession): Активная сессия с БД.

        """

        if isinstance(model, list):
            for item in model:
                session.add(item)

        else:
            session.add(model)

        await session.commit()

    @staticmethod
    async def update_data_in_db(
        model: SQLModel,
        session: AsyncSession,
        key: Any,
        value: Any,
    ) -> None:
        """DocString."""

        await session.execute(
            update(
                model,
                values={key: value}
            )
        )
        await session.commit()

    async def get_data_by_id(
        self,
        key: str,
    ) -> str:
        """Метод возвращает запись по id."""

        data = await self.cache_handler.get_by_id(
            key=key,
        )

        return data

    async def set_data_by_id(
        self,
        key: str,
        value: str,
    ) -> None:

        await self.cache_handler.set_by_id(
            key=key,
            value=value
        )
