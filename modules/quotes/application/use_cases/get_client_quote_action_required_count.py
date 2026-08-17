from modules.quotes.application.results.get_client_quote_action_required_count_result import (
    GetClientQuoteActionRequiredCountResult,
)


class GetClientQuoteActionRequiredCountUseCase:

    def __init__(
        self,
        quote_repository,
    ):
        self.quote_repository = quote_repository

    def execute(
        self,
        user_id: str,
    ) -> GetClientQuoteActionRequiredCountResult:

        count = (
            self.quote_repository
            .count_action_required_by_customer(
                user_id
            )
        )

        return GetClientQuoteActionRequiredCountResult(
            count=count
        )