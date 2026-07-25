from core.exceptions import DomainException

class LeadNotFound(DomainException):

    def __init__(self):
        super().__init__(
            message="Le prospect n'existe pas.",
            status_code=404,
        )
class LeadHasActiveQuote(DomainException):

    def __init__(self):
        super().__init__(
            "Ce client possède déjà une offre active.",
            400
        )
class LeadAlreadyAssigned(DomainException):

    def __init__(self):
        super().__init__(
            message="Ce prospect est déjà attribué à un commercial.",
            status_code=400,
        )

class InvalidLeadState(DomainException):

    def __init__(self):
        super().__init__(
            messagee="Ce prospect ne peut pas être attribué dans son état actuel.",
            status_code=400,
        )

class CannotContactLead(DomainException):

    def __init__(self):
        super().__init__(
            message="Seuls les prospects assignés peuvent être marqués comme contactés.",
            status_code=400,
        )

class LeadAccessDenied(DomainException):

    def __init__(self):

        super().__init__(
            message="Vous n'êtes pas autorisé à modifier ce prospect.",
            status_code=403,
        )

class ActiveLeadAlreadyExists(DomainException):

    def __init__(self):

        super().__init__(
            message=(
                "Vous avez déjà une demande en cours pour ce véhicule."
            ),
            status_code=409,
        )

class LeadCannotBeAssigned(DomainException):

    def __init__(self):

        super().__init__(
            "Ce lead ne peut pas être assigné.",
            400
        )

class LeadCannotBeDeleted(DomainException):

    def __init__(self):

        super().__init__(
            message=(
                "Ce prospect ne peut pas être supprimé."
            ),
            status_code=400,
        )