from core.exceptions import DomainException

class VehicleNotEligibleForInspection(DomainException):
    def __init__(self):
        super().__init__(
            message="Ce véhicule n'est pas éligible à une inspection.",
            status_code=400
        )

class VehicleNotFound(DomainException):
    def __init__(self):
        super().__init__(
            message="Véhicule introuvable.",
            status_code=404
        )

class VehicleNotReadyForPublication(DomainException):
    def __init__(self):
        super().__init__(
            message="Le véhicule n'est pas prêt à être publié",
            status_code=400
        )
class VehicleAlreadyPublished(DomainException):
    def __init__(self):
        super().__init__(
            message="Le véhicule est déjà publié",
            status_code=400
        )

class VehicleCannotChangeAvailability(DomainException):
    def __init__(self):
        super().__init__(
            "La disponibilité d'un véhicule vendu ne peut pas être modifiée.",
            400,
        )

class VehicleAvailabilityAlreadySet(DomainException):
    def __init__(self):
        super().__init__(
            message="La disponibilité est déjà dans cet état",
            status_code=400
        )

class VehicleNotAvailable(DomainException):
    def __init__(self):
        super().__init__(
            message="Véhicule indisponible",
            status_code=400
        )


class VehicleAlreadyExists(DomainException):
    def __init__(self):
        super().__init__("Un véhicule avec cette immatriculation existe déjà")

class InvalidVehicleType(DomainException):
    def __init__(self):
        super().__init__(
            message="Type de véhicule invalide",
            status_code=400
        )
        
class VehicleCannotBeMarkedAsInspected(DomainException):

    def __init__(self):

        super().__init__(
            message=(
                "Ce véhicule ne peut pas être marqué comme inspecté."
            ),
            status_code=400,
        )

class VehicleNotEligibleForReconditioning(DomainException):

    def __init__(self):

        super().__init__(
            message=(
                "Le véhicule n'est pas éligible au reconditionnement."
            ),
            status_code=400,
        )



class VehicleCannotStartReconditioning(DomainException):

    def __init__(self):

        super().__init__(
            message=(
                "Impossible de démarrer le reconditionnement pour ce véhicule."
            ),
            status_code=400,
        )



class VehicleCannotBeMarkedAsReconditioned(DomainException):

    def __init__(self):

        super().__init__(
            message=(
                "Ce véhicule ne peut pas être marqué comme reconditionné."
            ),
            status_code=400,
        )



class VehicleCannotBeMarkedAsReady(DomainException):

    def __init__(self):

        super().__init__(
            message=(
                "Ce véhicule ne peut pas être marqué comme prêt."
            ),
            status_code=400,
        )

class VehicleNotReadyForFinalCheck(DomainException):

    def __init__(self):

        super().__init__(
            message=(
                "Ce véhicule n'est pas prêt pour le contrôle final."
            ),
            status_code=400,
        )
        

class VehicleCannotBePublished(DomainException):

    def __init__(self):

        super().__init__(
            message=(
                "Ce véhicule ne peut pas être publié."
            ),
            status_code=400,
        )

class VehicleNotAvailableForTestDrive(DomainException):

    def __init__(self):

        super().__init__(
            message=(
                "Ce véhicule n'est pas disponible "
                "pour un essai routier."
            ),
            status_code=400,
        )