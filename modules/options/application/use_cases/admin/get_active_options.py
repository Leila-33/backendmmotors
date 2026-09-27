from modules.options.application.results.admin.get_active_options_result import (
    GetActiveOptionsResult,
)


class GetActiveOptionsUseCase:
    """
    Récupère les options actuellement actives.
    """
    def __init__(
        self,
        option_repository,
    ):
        self.option_repository = option_repository

    def execute(self) -> GetActiveOptionsResult:

        options = (
            self.option_repository
            .get_active()
        )

        return GetActiveOptionsResult(
            options=options
        )