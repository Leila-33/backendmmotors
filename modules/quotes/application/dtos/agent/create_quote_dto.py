from dataclasses import dataclass

from modules.financing.domain.inputs.trade_in_input import (
    TradeInInput,
)


@dataclass
class CreateQuoteDTO:

    lead_id: str

    agent_id: str

    discount: float

    down_payment: float

    duration_months: int

    trade_in: TradeInInput | None = None