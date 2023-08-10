import asyncio
from websockets.server import serve, WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedError
from src.models.ws import Connection, Message
from src.core.logger import logger
from src.core.config import settings

active_connections: list[Connection] = []


async def welcome(websocket: WebSocketServerProtocol, user_id: str) -> str:
    active_connections.append(
        Connection(
            user_id=user_id.strip("/"),
            websocket=websocket
        )
    )
    logger.info("Подключен новый пользователь")


async def receiver(websocket: WebSocketServerProtocol, user_id: str) -> None:
    await welcome(websocket, user_id)
    try:
        while True:
            message = Message.parse_raw((await websocket.recv()).strip())
            if message.broadcast:
                for con in active_connections:
                    await con.websocket.send(message.text)
            else:
                for con in [
                    i for i in active_connections
                    if i.user_id == message.user_id
                ]:
                    await con.websocket.send(message.text)
    except ConnectionClosedError:
        con = next(i for i in active_connections if i.websocket == websocket)
        active_connections.remove(con)
        logger.info("Пользователь отключен")


async def main():
    async with serve(receiver, settings.ws_host, settings.ws_port):
        await asyncio.Future()


if __name__ == "__main__":
    logger.info("Сервис запущен")
    asyncio.run(main())
