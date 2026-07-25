from core.exceptions import DomainException

class ReconditioningNotFound(DomainException):
    def __init__(self):
        super().__init__(
            message="Reconditionnement introuvable pour ce véhicule",
            status_code=404
        )



class InvalidRepairConfiguration(DomainException):
    def __init__(self, code: str):
        super().__init__(
            message=f"Le code de réparation '{code}' n'est pas configuré.",
            status_code=500
        )
        
class ReconditioningNotCompleted(DomainException):
    def __init__(self):
        super().__init__(
            message="Le reconditionnement n'est pas terminé",
            status_code=400
        )

class ReconditioningAlreadyRunning(DomainException):
    def __init__(self):
        super().__init__(
            message="Un reconditionnement est déjà en cours pour ce véhicule.",
            status_code=409
        )

class ReconditioningCannotStart(DomainException):

    def __init__(self):

        super().__init__(
            message=(
                "Impossible de démarrer le reconditionnement."
            ),
            status_code=400,
        )



class ReconditioningCannotComplete(DomainException):

    def __init__(self):

        super().__init__(
            message=(
                "Impossible de terminer le reconditionnement."
            ),
            status_code=400,
        )



class ReconditioningCannotBeApproved(DomainException):

    def __init__(self):

        super().__init__(
            message=(
                "Le reconditionnement ne peut pas être approuvé."
            ),
            status_code=400,
        )