from core.exceptions import DomainException

class TestDriveStatusForbidden(DomainException):

    def __init__(self):

        super().__init__(
            "Les clients ne peuvent que annuler un essai routier",
            403
        )

class TestDriveSlotUnavailable(DomainException):
    def __init__(self):
        super().__init__(
            message="Ce créneau d'essai n'est plus disponible",
            status_code=409
        )

class TestDrivePastDate(DomainException):

    def __init__(self):

        super().__init__(
            "La date ne peut pas être dans le passé",
            400
        )

class TestDriveNotFound(DomainException):

    def __init__(self):

        super().__init__(
            "Essai routier introuvable",
            404
        )

class InvalidAvailabilityDate(DomainException):

    def __init__(self):

        super().__init__(
            "Date de disponibilité invalide",
            400
        )