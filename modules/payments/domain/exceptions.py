from core.exceptions import DomainException

class PaymentNotFound(DomainException):

    def __init__(self):

        super().__init__(
            "Paiement introuvable",
            404
        )

class PaymentNotAllowed(DomainException):

    def __init__(self):

        super().__init__(
            "Le dossier doit être approuvé avant paiement",
            400
        )