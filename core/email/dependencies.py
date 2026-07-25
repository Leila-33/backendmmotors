from core.email.services.smtp_email_service import SMTPEmailService


from core.config.settings import settings


def get_email_service():
    return SMTPEmailService(
        host=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        frontend_url=settings.FRONTEND_URL
    )
