from core.exceptions import DomainException

class InvalidTicketStatus(DomainException):
    def __init__(self):
        super().__init__(
            message="Statut de ticket invalide.",
            status_code=400
        )

class TicketClosedException(DomainException):
    def __init__(self):
        super().__init__(
            message="Impossible d'envoyer un message sur un ticket fermé.",
            status_code=400
        )

class SupportTicketNotFound(DomainException):
    def __init__(self):
        super().__init__(
            message="Ticket introuvable.",
            status_code=404
        )

class TicketAccessDenied(DomainException):
    def __init__(self):
        super().__init__(
            message="Accès refusé à ce ticket.",
            status_code=403
        )

class InvalidTicketState(DomainException):
    def __init__(self):
        super().__init__(
            message="Seuls les tickets résolus ou fermés peuvent être archivés.",
            status_code=400,
        )

class EmptyMessageException(DomainException):
    def __init__(self):
        super().__init__(
            message="Le message ne peut pas être vide.",
            status_code=400
        )

class MessageTooLongException(DomainException):
    def __init__(self, max_length: int = 2000):
        super().__init__(
            message=f"Le message dépasse la limite autorisée ({max_length} caractères).",
            status_code=400
        )