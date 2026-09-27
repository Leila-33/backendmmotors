from modules.options.application.results.admin.get_options_result import (
    GetOptionsResult,
)


class GetOptionsUseCase:
    """
    Récupère l'ensemble des options disponibles, actives ou désactivées.
    """
    def __init__(
        self,
        option_repository,
    ):
        self.option_repository = option_repository

    def execute(self) -> GetOptionsResult:

        options = (
            self.option_repository
            .get_all()
        )

        return GetOptionsResult(
            options=options
        )