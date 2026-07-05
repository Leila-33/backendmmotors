from core.services.smtp_email_service import SMTPEmailService


from core.config import settings


def get_email_service():
    return SMTPEmailService(
        host=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        frontend_url=settings.FRONTEND_URL
    )


from core.config import settings

from core.security.jwt_service import JwtService

def get_jwt_service():
    return JwtService(
        secret=settings.JWT_SECRET,
        algorithm="HS256"
    )