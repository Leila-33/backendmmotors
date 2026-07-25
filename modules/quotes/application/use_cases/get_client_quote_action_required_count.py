from modules.quotes.api.schemas import QuoteActionRequiredCountResponse

class GetClientQuoteActionRequiredCountUseCase:


    def __init__(
        self,
        quote_repository,
    ):

        self.quote_repository = quote_repository



    def execute(
        self,
        user_id: str,
    ):

        count = (
            self.quote_repository
            .count_action_required_by_customer(
                user_id
            )
        )


        return QuoteActionRequiredCountResponse(
            count=count
        )