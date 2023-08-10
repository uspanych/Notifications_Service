from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.postgres import get_session
from models.notifications import LikeModel, NewSeriesModel, VerifyUserModel
from services.notifications import (FastNotificationsService,
                                    get_notifications_service)
from models.ws import Message
from services.ws_client import send_ws_message


router = APIRouter()


@router.post(
    '/new_series',
    description='Метод создает уведомление о новой серии',
)
async def create_new_series_notification(
    series: NewSeriesModel = Body(),
    session: AsyncSession = Depends(get_session),
    service: FastNotificationsService = Depends(get_notifications_service),
) -> None:

    await service.check_new_series(
        session=session,
        new_series=series,
    )


@router.post(
    '/verify',
    description='Метод создает уведомление о подтверждении регистрации',
)
async def create_event_verify(
    verify_user: VerifyUserModel,
    service: FastNotificationsService = Depends(get_notifications_service),
) -> None:

    await service.verify_email(
        new_verify=verify_user,
    )


@router.post(
    '/new_like',
    description='Метод создает уведомление о новых лайках',
)
async def create_likes_notification(
    like: LikeModel = Body(),
    service: FastNotificationsService = Depends(get_notifications_service),
) -> None:

    await service.like_event(
        new_like=like,
    )


@router.post(
    "/new_fast_notify",
    description="Метод для отправки сообщения по вебсокету"
)
async def fast_notify(
    message: Message = Body()
) -> None:
    send_ws_message(message=message)
