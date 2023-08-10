from models.base import BaseOrjsonModel


class Message(BaseOrjsonModel):
    user_id: str
    text: str
    broadcast: bool = False
