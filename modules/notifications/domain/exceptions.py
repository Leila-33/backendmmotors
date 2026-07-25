from core.exceptions import DomainException

class NotificationNotFound(DomainException):

    def __init__(self):

        super().__init__(
            "Notification introuvable",
            404
        )


class InvalidNotificationType(DomainException):

    def __init__(self, notif_type: str):

        super().__init__(
            f"Type de notification invalide : {notif_type}",
            400
        )

class InvalidNotificationEntityType(DomainException):

    def __init__(self, entity_type: str):

        super().__init__(
            message=(
                f"Type d'entité de notification invalide : "
                f"{entity_type}."
            ),
            status_code=400,
        )