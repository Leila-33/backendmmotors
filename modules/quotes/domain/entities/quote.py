from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from modules.quotes.domain.enums import QuoteStatus
from modules.quotes.domain.exceptions import (
    QuoteCannotBeSent,
    QuoteAlreadySent,
    QuoteAlreadyAccepted,
    QuoteCannotBeAccepted,
    QuoteAlreadyRefused,
    QuoteCannotBeRefused,
    QuoteRefusalReasonRequired,
    QuoteCannotBeModified
)
from modules.quotes.domain.enums import QuoteRefusalReason

@dataclass
class Quote:

    id: str

    lead_id: str

    base_price: float

    created_at: datetime = field(
        default_factory=lambda:
        datetime.now(timezone.utc)
    )

    discount: float = 0

    down_payment: float = 0

    trade_in_value: int = 0

    financed_amount: float = 0

    duration_months: int = 36

    monthly_payment: float = 0

    status: QuoteStatus = QuoteStatus.DRAFT

    sent_at: datetime | None = None

    accepted_at: datetime | None = None
    
    refusal_reason: QuoteRefusalReason | None = None

    refusal_comment: str | None = None

    refused_at: datetime | None = None
    expires_at: datetime | None = None

    lead: object = None

    trade_in: object | None = None





    def send(self):

        if self.status != QuoteStatus.DRAFT:
            raise QuoteCannotBeSent()

        self.status = QuoteStatus.SENT

        self.sent_at = datetime.now(timezone.utc)
        self.expires_at = (
        datetime.now(timezone.utc)
        + timedelta(days=30)
    )
        
    def is_expired(self) -> bool:

        if not self.expires_at:
            return False

        return (
            datetime.now(timezone.utc)
            > self.expires_at
        )

    def expire(self):

        if self.status == QuoteStatus.SENT:

            self.status = QuoteStatus.EXPIRED


    def accept(self):


        if self.status == QuoteStatus.ACCEPTED:

            raise QuoteAlreadyAccepted()



        if self.status != QuoteStatus.SENT:

            raise QuoteCannotBeAccepted()



        self.status = QuoteStatus.ACCEPTED


        self.accepted_at = datetime.now(
            timezone.utc
        )


    def refuse(
    self,
    reason,
    comment=None,
):


        if self.status == QuoteStatus.REJECTED:

            raise QuoteAlreadyRefused()



        if self.status != QuoteStatus.SENT:

            raise QuoteCannotBeRefused()



        if reason is None:

            raise QuoteRefusalReasonRequired()



        self.status = QuoteStatus.REJECTED


        self.refusal_reason = reason


        self.refusal_comment = comment


        self.refused_at = datetime.now(
            timezone.utc
        )
        

    def can_be_viewed_by_customer(self) -> bool:

        return self.status in [
            QuoteStatus.SENT,
            QuoteStatus.ACCEPTED,
            QuoteStatus.REJECTED,
        ]
    
    def update_financing(
    self,
    base_price,
    discount,
    down_payment,
    trade_in_value,
    duration_months,
    financed_amount,
    monthly_payment,
):

        if self.status != QuoteStatus.DRAFT:
            raise QuoteCannotBeModified()


        self.base_price = base_price

        self.discount = discount

        self.down_payment = down_payment

        self.trade_in_value = trade_in_value

        self.duration_months = duration_months

        self.financed_amount = financed_amount

        self.monthly_payment = monthly_payment

    def can_be_deleted(self) -> bool:

        return (
            self.status == QuoteStatus.DRAFT
        )