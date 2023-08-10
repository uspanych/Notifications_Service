import asyncio
from typing import Any, Callable

import orjson
from aio_pika import DeliveryMode, Exchange, ExchangeType, connect_robust
from aio_pika.abc import AbstractIncomingMessage, AbstractQueue
from aio_pika.channel import Channel
from aio_pika.connection import Connection
from aio_pika.message import Message

from src.core.logger import logger


class RMQ:
    def __init__(self) -> None:
        self.connection: Connection | None = None
        self.channel: Channel | None = None
        self.exchange: Exchange | None = None
        self.queue: AbstractQueue | None = None

        self.funcs: dict = {}

    async def connect(
        self,
        url: str,
        queue_name: str,
        topic_name: str = "topic_v1"
    ):
        self.topic_name = topic_name
        self.connection = await connect_robust(
            url=url,
            loop=asyncio.get_running_loop()
        )

        self.channel = await self.connection.channel()

        self.exchange = await self.channel.declare_exchange(
            self.topic_name,
            ExchangeType.TOPIC
        )
        self.queue = await self.channel.declare_queue(queue_name, durable=True)

    async def send(
        self,
        routing_key: str,
        data: dict,
        correlation_id,
    ) -> None:

        message = Message(
            body=self._serialize(data),
            content_type="application/json",
            correlation_id=correlation_id,
            delivery_mode=DeliveryMode.PERSISTENT
        )
        await self.exchange.publish(message, routing_key, timeout=10)

    async def consume_queue(
            self,
            func: Callable,
            task_id: int,
            binding_keys: str | list[str]
    ):
        if isinstance(binding_keys, list):
            for binding_key in binding_keys:
                await self.queue.bind(self.exchange, routing_key=binding_key)
        elif isinstance(binding_keys, str):
            await self.queue.bind(self.exchange, routing_key=binding_keys)

        self.funcs.update({
            task_id: func
        })

    async def start_iterator(self):
        async with self.queue.iterator() as iterator:
            message: AbstractIncomingMessage
            async for message in iterator:
                async with message.process(ignore_processed=True):
                    body: dict = self._deserialize(message.body)
                    task_id = body.pop("task_id")
                    logger.info("Получено новое сообщение в очереди")
                    await self.funcs[task_id](message)

    @staticmethod
    def _serialize(data: Any) -> bytes:
        return orjson.dumps(data)

    @staticmethod
    def _deserialize(data: bytes) -> Any:
        return orjson.loads(data)

    async def close(self):
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()


rabbit: RMQ | None = None


async def get_rabbit() -> RMQ:
    return rabbit
