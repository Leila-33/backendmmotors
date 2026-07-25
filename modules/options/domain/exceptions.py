from core.exceptions import DomainException

class OptionNotAllowed(DomainException):
    def __init__(self, option_id: str):
        super().__init__(
            message=f"Option non autorisée : {option_id}",
            status_code=400
        )

class OptionNotFound(DomainException):
    def __init__(self):
        super().__init__(
            message="Option introuvable",
            status_code=404
        )

class OptionAlreadyExists(DomainException):

    def __init__(
        self,
        name: str,
    ):

        super().__init__(
            message=f"L'option '{name}' existe déjà",
            status_code=409
        )

class SystemOptionCannotBeModified(DomainException):

    def __init__(self):
        super().__init__(
            message="Les options système ne peuvent pas être modifiées.",
            status_code=400
        )