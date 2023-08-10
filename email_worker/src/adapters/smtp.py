from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
import jinja2
from aio_pika.abc import AbstractIncomingMessage

from src.core.config import BASE_DIR

from ..models.notifications import LikeModel, NewSeriesModel, VerifyUserModel


class SmtpWorker:
    def __init__(
        self,
        smtp_address: str,
        smtp_port: int,
        smtp_login: str,
        smtp_password: str,
        smtp_use_tls: bool,
        smtp_sender: str
    ) -> None:
        self.smtp_address = smtp_address
        self.smtp_port = smtp_port
        self.smtp_login = smtp_login
        self.smtp_password = smtp_password
        self.smtp_use_tls = smtp_use_tls
        self.smtp_sender = smtp_sender

        self.environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(BASE_DIR/"templates/")
        )

    async def _send(self, content: str, recipients: list[str], subject: str):

        message = MIMEMultipart()
        message["From"] = self.smtp_sender
        message["To"] = ", ".join(recipients)
        message["Subject"] = subject
        html_message = MIMEText(content, 'html')
        message.attach(html_message)

        await aiosmtplib.send(
            message,
            username=self.smtp_login,
            password=self.smtp_password,
            sender=self.smtp_sender,
            recipients=recipients,
            hostname=self.smtp_address,
            port=self.smtp_port,
            start_tls=self.smtp_use_tls
        )

    async def send_likes(self, message: AbstractIncomingMessage):
        body = LikeModel.parse_raw(message.body)
        template = self.environment.get_template("likes.html")
        content = template.render(
            likes=body.likes,
            target=body.target,
        )
        await self._send(
            content=content,
            subject="Получены новые лайки!",
            recipients=[body.email],
        )
        await message.ack()

    async def send_new_series(self, message: AbstractIncomingMessage):
        body = NewSeriesModel.parse_raw(message.body)
        template = self.environment.get_template("new_series.html")
        content = template.render(
            movie_name=body.movie_name,
            user_name=body.user_name,
        )
        await self._send(
            content=content,
            subject="Вышла новая серия!",
            recipients=[body.user_email]
        )

        await message.ack()

    async def send_verify(self, message: AbstractIncomingMessage):
        body = VerifyUserModel.parse_raw(message.body)
        template = self.environment.get_template("verify.html")
        content = template.render(
            user_name=body.user_name,
        )
        await self._send(
            content=content,
            subject="Ваша почта подтверждена!",
            recipients=[body.user_email]
        )
        await message.ack()
        