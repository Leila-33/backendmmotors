from modules.quotes.application.results.get_client_quote_action_required_count_result import (
    GetClientQuoteActionRequiredCountResult,
)
from modules.quotes.application.dtos.customer_id_dto import (
    CustomerIdDto,
)

class GetClientQuoteActionRequiredCountUseCase:

    def __init__(
        self,
        quote_repository,
    ):
        self.quote_repository = quote_repository

    def execute(
        self,
        dto: CustomerIdDto,
    ) -> GetClientQuoteActionRequiredCountResult:

        count = (
            self.quote_repository
            .count_action_required_by_customer(
                dto.customer_id
            )
        )

        return GetClientQuoteActionRequiredCountResult(
            count=count
        )