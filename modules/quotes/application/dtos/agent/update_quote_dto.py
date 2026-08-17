from dataclasses import dataclass

from modules.financing.domain.inputs.trade_in_input import (
    TradeInInput,
)


@dataclass
class UpdateQuoteDTO:

    quote_id: str

    discount: float

    down_payment: float

    duration_months: int

    trade_in: TradeInInput | None

    agent_id: str