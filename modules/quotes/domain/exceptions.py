from core.exceptions import DomainException

class QuoteNotFound(DomainException):

    def __init__(self):

        super().__init__(
            message="Offre introuvable.",
            status_code=404,
        )


class QuoteCannotBeSent(DomainException):

    def __init__(self):
        super().__init__(
            message="Seules les offres en brouillon peuvent être envoyées.",
            status_code=400,
        )

class QuoteAlreadySent(DomainException):

    def __init__(self):

        super().__init__(
            message=(
                "Cette offre a déjà été envoyée au client."
            ),
            status_code=400,
        )

class QuoteCannotBeAccepted(DomainException):

    def __init__(self):

        super().__init__(
            message=(
                "Cette offre ne peut pas être acceptée."
            ),
            status_code=400,
        )

class QuoteAlreadyAccepted(DomainException):

    def __init__(self):

        super().__init__(
            message=(
                "Cette offre a déjà été acceptée."
            ),
            status_code=400,
        )

class QuoteCannotBeRefused(DomainException):

    def __init__(self):

        super().__init__(
            message=(
                "Cette offre ne peut pas être refusée."
            ),
            status_code=400,
        )

class QuoteAlreadyRefused(DomainException):

    def __init__(self):

        super().__init__(
            message=(
                "Cette offre a déjà été refusée."
            ),
            status_code=400,
        )

class QuoteRefusalReasonRequired(DomainException):

    def __init__(self):

        super().__init__(
            message=(
                "Un motif de refus est obligatoire."
            ),
            status_code=400,
        )

class QuoteNotAvailableForCustomer(DomainException):

    def __init__(self):

        super().__init__(
            "Cette offre n'est pas disponible.",
            403
        )

class QuoteCannotBeModified(DomainException):

    def __init__(self):

        super().__init__(
            message=(
                "Seules les offres en brouillon peuvent être modifiées."
            ),
            status_code=400,
        )
        
class QuoteCannotBeDeleted(DomainException):

    def __init__(self):

        super().__init__(
            message=(
                "Cette offre ne peut pas être supprimée."
            ),
            status_code=400,
        )
