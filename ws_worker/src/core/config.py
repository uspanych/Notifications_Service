from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    ws_host: str = "0.0.0.0"
    ws_port: int = Field(8765, env="WS_PORT")

    sentry_dsn: str = Field(..., env="WS_SENTRY_DSN")


settings = Settings()
