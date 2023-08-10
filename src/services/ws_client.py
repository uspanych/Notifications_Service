from websockets.sync.client import connect
from core.config import settings
from models.ws import Message


def send_ws_message(message: Message) -> None:
    with connect(f"ws://{settings.ws_host}:{settings.ws_port}") as websocket:
        websocket.send(message.json())
