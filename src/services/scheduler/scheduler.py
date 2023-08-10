from apscheduler.schedulers.asyncio import AsyncIOScheduler


app_scheduler: AsyncIOScheduler | None = None


async def get_scheduler() -> AsyncIOScheduler:
    return app_scheduler
