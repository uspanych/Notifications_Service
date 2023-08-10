import orjson
from sqlmodel import SQLModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseOrjsonModel(SQLModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
