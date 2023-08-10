from src.adapters.rabbit import RMQ
from src.adapters.smtp import SmtpWorker
from src.core.config import settings
from src.core.logger import logger

import asyncio


async def main():
    rabbit = RMQ()
    smtp = SmtpWorker(
        settings.smtp_address,
        settings.smtp_port,
        settings.smtp_login,
        settings.smtp_password,
        settings.smtp_use_tls,
        settings.smtp_sender
    )

    await rabbit.connect(settings.get_amqp_uri(), queue_name="email_worker")

    await rabbit.consume_queue(func=smtp.send_likes, binding_keys="event.like", task_id=1)
    await rabbit.consume_queue(func=smtp.send_new_series, binding_keys="event.series", task_id=2)
    await rabbit.consume_queue(func=smtp.send_verify, binding_keys="event.verify", task_id=3)

    await rabbit.start_iterator()


if __name__ == "__main__":
    logger.info("Сервис запустился")
    asyncio.run(main())
