from core.exceptions import DomainException

class InspectionAlreadyRunning(DomainException):
    def __init__(self):
        super().__init__(
            message="Une inspection est déjà en cours pour ce véhicule.",
            status_code=409
        )

class InspectionAlreadyCompleted(DomainException):
    def __init__(self):
        super().__init__(
            message="Ce véhicule a déjà été inspecté.",
            status_code=409
        )

class InspectionNotFound(DomainException):
    def __init__(self):
        super().__init__(
            message="Inspection introuvable.",
            status_code=404
        )

class InspectionNotCompleted(DomainException):
    def __init__(self):
        super().__init__(
            message="L'inspection doit être terminée avant de lancer le reconditionnement.",
            status_code=400
        )

class InspectionCannotBeStarted(DomainException):

    def __init__(self):

        super().__init__(
            message="Cette inspection ne peut pas être démarrée.",
            status_code=400,
        )