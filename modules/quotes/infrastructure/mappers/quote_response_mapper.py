
from modules.quotes.application.results.agent.create_quote_result import (
    CreateQuoteResult,
)
from modules.quotes.application.results.agent.get_quote_detail_result import (
    GetQuoteDetailResult,
)
from modules.quotes.application.results.get_customer_quotes_result import (
    GetCustomerQuotesResult,
)
from modules.quotes.application.results.get_customer_quote_detail_result import (
    GetCustomerQuoteDetailResult,
)
from modules.quotes.application.results.quote_action_result import (
    QuoteActionResult,
)
from modules.quotes.application.results.accept_quote_result import (
    AcceptQuoteResult,
)
from modules.quotes.application.results.get_client_quote_action_required_count_result import (
    GetClientQuoteActionRequiredCountResult,
)

from modules.quotes.api.schemas import (
    CreateQuoteResponse,
    QuoteDetailResponse,
    CustomerQuoteListResponse,
    QuoteCustomerDetailResponse,
    QuoteActionResponse,
    AcceptQuoteResponse,
    QuoteActionRequiredCountResponse,
)

from modules.quotes.domain.enums import QuoteStatus
from modules.vehicles.infrastructure.mappers.vehicle_response_mapper import (
    VehicleResponseMapper,
)


class QuoteResponseMapper:
    
    def __init__(
            self,
            vehicle_response_mapper: VehicleResponseMapper,
        ):
            self.vehicle_response_mapper = (
                vehicle_response_mapper
            )

        # =====================================================
    # CREATE
    # =====================================================

    @staticmethod
    def to_create_response(
        result: CreateQuoteResult,
    ) -> CreateQuoteResponse:

        return CreateQuoteResponse(
            quote_id=result.quote_id,
            lead_id=result.lead_id,
            vehicle_id=result.vehicle_id,
            message=result.message,
        )


    # =====================================================
    # COMMON - DETAIL DATA
    # =====================================================


    @staticmethod
    def _get_status_value(status):
        return (
            status.value
            if hasattr(status, "value")
            else status
        )

    def _to_common_detail_data(self, quote) -> dict:
        vehicle = quote.lead.vehicle

        return {
            "id": quote.id,
            "status": self._get_status_value(quote.status),
            "base_price": quote.base_price,
            "discount": quote.discount,
            "down_payment": quote.down_payment,
            "trade_in_value": quote.trade_in_value,
            "financed_amount": quote.financed_amount,
            "duration_months": quote.duration_months,
            "monthly_payment": quote.monthly_payment,
            "vehicle": {
                "id": vehicle.id,
                "brand": vehicle.brand,
                "model": vehicle.model,
                "price": vehicle.price,
                "year": vehicle.year,
                "mileage": vehicle.mileage,
                "engine_type": vehicle.engine_type,
                "images": self.vehicle_response_mapper.map_images(
                    vehicle.images
                ),
            },
            "trade_in": (
                {
                    "brand": quote.trade_in.brand,
                    "model": quote.trade_in.model,
                    "year": quote.trade_in.year,
                    "mileage": quote.trade_in.mileage,
                    "condition": quote.trade_in.condition,
                    "estimated_value": (
                        quote.trade_in.estimated_value
                    ),
                }
                if quote.trade_in
                else None
            ),
            "created_at": quote.created_at,
            "sent_at": quote.sent_at,
            "accepted_at": quote.accepted_at,
            "refusal_reason": quote.refusal_reason,
            "refusal_comment": quote.refusal_comment,
            "refused_at": quote.refused_at,
            "expires_at": quote.expires_at,
        }


    # =====================================================
    # CUSTOMER - DETAIL
    # =====================================================
    def to_customer_detail_response(
    self,
    result: GetCustomerQuoteDetailResult,
) -> QuoteCustomerDetailResponse:
        return QuoteCustomerDetailResponse(
            **self._to_common_detail_data(result.quote),
            application_id=result.application_id,
            sales_agent=(
                {
                    "id": result.quote.lead.assigned_agent.id,
                    "first_name": (
                        result.quote.lead.assigned_agent.first_name
                    ),
                    "last_name": (
                        result.quote.lead.assigned_agent.last_name
                    ),
                }
                if result.quote.lead.assigned_agent
                else None
            ),
        )
    
    # =====================================================
    # AGENT - DETAIL
    # =====================================================
    def to_detail_response(
        self,
        result: GetQuoteDetailResult,
    ) -> QuoteDetailResponse:
        quote = result.quote
        lead = quote.lead

        return QuoteDetailResponse(
            **self._to_common_detail_data(quote),
            lead={
                "id": lead.id,
                "first_name": lead.first_name,
                "last_name": lead.last_name,
                "email": lead.email,
                "phone": lead.phone,
            },
        )

    # =====================================================
    # CUSTOMER - LIST
    # =====================================================
    @staticmethod
    def to_list_response(
        quote,
    ) -> CustomerQuoteListResponse:

        return CustomerQuoteListResponse(
            id=quote.id,

            status=(
                quote.status.value
                if hasattr(
                    quote.status,
                    "value",
                )
                else quote.status
            ),

            base_price=quote.base_price,
            monthly_payment=quote.monthly_payment,
            created_at=quote.created_at,

            vehicle={
                "id": quote.lead.vehicle.id,
                "brand": quote.lead.vehicle.brand,
                "model": quote.lead.vehicle.model,
                "price": quote.lead.vehicle.price,
            },

            requires_action=(
                quote.status == QuoteStatus.SENT
            ),
        )

    @staticmethod
    def to_customer_list_response(
        result: GetCustomerQuotesResult,
    ) -> list[CustomerQuoteListResponse]:

        return [
            QuoteResponseMapper.to_list_response(
                quote
            )
            for quote in result.quotes
        ]




    # =====================================================
    # GENERIC ACTION
    # =====================================================

    @staticmethod
    def to_action_response(
        result: QuoteActionResult,
    ) -> QuoteActionResponse:

        return QuoteActionResponse(
            id=result.quote_id,
            message=result.message,
        )

    # =====================================================
    # CUSTOMER - ACCEPT
    # =====================================================

    @staticmethod
    def to_accept_response(
        result: AcceptQuoteResult,
    ) -> AcceptQuoteResponse:

        return AcceptQuoteResponse(
            quote_id=result.quote_id,
            application_id=result.application_id,
            message=result.message,
        )

    # =====================================================
    # CUSTOMER - ACTION REQUIRED COUNT
    # =====================================================

    @staticmethod
    def to_action_required_count_response(
        result: GetClientQuoteActionRequiredCountResult,
    ) -> QuoteActionRequiredCountResponse:

        return QuoteActionRequiredCountResponse(
            count=result.count,
        )