from fastapi import Depends, HTTPException
import os

# =====================
# REPOSITORIES
# =====================

def get_application_repository():
    from modules.applications.infrastructure.repositories.application_repository_sql import ApplicationRepositorySQL
    return ApplicationRepositorySQL()


def get_event_repository():
    from modules.applications.infrastructure.repositories.event_repository_sql import EventRepositorySQL
    return EventRepositorySQL()


# =====================
# SERVICES
# =====================

def get_notification_service():
    from modules.notifications.infrastructure.repositories.notification_repository_sql import NotificationRepositorySQL
    from modules.notifications.application.services.notification_service import NotificationService
    from modules.shared.infrastructure.email.smtp_email_service import SMTPEmailService

    notification_repo = NotificationRepositorySQL()

    email_service = SMTPEmailService(
        host=os.getenv("SMTP_HOST"),
        port=int(os.getenv("SMTP_PORT")),
        username=os.getenv("SMTP_USER"),
        password=os.getenv("SMTP_PASSWORD")
    )

    return NotificationService(notification_repo, email_service)

