from pydantic import BaseSettings, Field
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.absolute()


class TestSettings(BaseSettings):
    smtp_address: str = Field(..., env="SMTP_ADDRESS")
    smtp_port: int = Field(..., env="SMTP_PORT")
    smtp_sender: str = Field(..., env='SMTP_SENDER')
    smtp_login: str = Field(..., env="SMTP_LOGIN")
    smtp_password: str = Field(..., env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(False, env="SMTP_USE_TLS")
    service_url: str = Field(..., env='SERVICE_URL')
    smtp_url: str = Field(..., env="SMTP_URL")

    class Config:
        env_file = BASE_DIR/".env"


test_settings = TestSettings()
