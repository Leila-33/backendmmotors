from core.exceptions import DomainException

class PaymentNotFound(DomainException):

    def __init__(self):

        super().__init__(
            "Paiement introuvable",
            404
        )

class PaymentNotAllowed(DomainException):

    def __init__(
        self,
        message: str = "Le dossier doit être approuvé avant paiement",
    ):
        super().__init__(
            message,
            400,
        )


class PaymentInvalid(DomainException):

    def __init__(
        self,
        message: str = "Le paiement est invalide.",
    ):
        self.message = message
        super().__init__(self.message)