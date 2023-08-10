from src.models.base import BaseOrjsonModel
from typing import Any


class Connection(BaseOrjsonModel):
    user_id: str
    websocket: Any


class Message(BaseOrjsonModel):
    user_id: str
    text: str
    broadcast: bool = False
