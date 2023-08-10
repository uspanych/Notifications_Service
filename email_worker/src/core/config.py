from pathlib import Path

from pydantic import BaseSettings, Field

BASE_DIR = Path(__file__).parent.parent.parent.absolute()


class Settings(BaseSettings):
    smtp_address: str = Field(..., env="SMTP_ADDRESS")
    smtp_port: int = Field(..., env="SMTP_PORT")
    smtp_sender: str = Field(..., env='SMTP_SENDER')
    smtp_login: str = Field(..., env="SMTP_LOGIN")
    smtp_password: str = Field(..., env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(False, env="SMTP_USE_TLS")

    rabbit_host: str = Field(..., env="RABBIT_HOST")
    rabbit_port: str = Field(..., env="RABBIT_PORT")
    rabbit_user: str = Field(..., env="RABBIT_USER")
    rabbit_pass: str = Field(..., env="RABBIT_PASS")

    ws_host: str = Field("0.0.0.0", env="WS_HOST")
    ws_port: int = Field(8765, env="WS_PORT")

    worker_sentry_dsn: str = Field(..., env="WORKER_SENTRY_DSN")

    def get_amqp_uri(self):
        return "amqp://{user}:{password}@{host}:{port}/".format(
            user=self.rabbit_user,
            password=self.rabbit_pass,
            host=self.rabbit_host,
            port=self.rabbit_port
        )

    class Config:
        env_file = BASE_DIR/".env"


settings = Settings()
