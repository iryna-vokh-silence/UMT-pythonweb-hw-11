from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from config import settings

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

fast_mail = FastMail(mail_config)


async def send_verification_email(email: str, token: str):
    verify_url = f"http://localhost:8000/auth/verify/{token}"
    html = f"""
    <p>Дякуємо за реєстрацію!</p>
    <p>Для підтвердження вашої електронної пошти натисніть посилання:</p>
    <p><a href="{verify_url}">{verify_url}</a></p>
    <p>Посилання діє 24 години.</p>
    """
    message = MessageSchema(
        subject="Підтвердження email — Contacts App",
        recipients=[email],
        body=html,
        subtype=MessageType.html,
    )
    await fast_mail.send_message(message)
