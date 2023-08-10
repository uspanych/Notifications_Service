from models.notifications import LikeModel
from adapters.rabbit import get_rabbit
from .scheduler import get_scheduler
from adapters.redis import get_redis


async def create_event_like(
    new_like: LikeModel,
):
    rabbit = await get_rabbit()
    scheduler = await get_scheduler()
    redis = await get_redis()

    new_like_count = await redis.get(new_like.subject_id)

    await rabbit.send(
        data={
            'likes': new_like_count.decode(),
            'email': new_like.user_email,
            'target': new_like.like_subject,
            'task_id': 1
            },
        routing_key='event.like',
        correlation_id=new_like.subject_id,
    )

    scheduler.remove_job(new_like.subject_id)
    await redis.delete(new_like.subject_id)
