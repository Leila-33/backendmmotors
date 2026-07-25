from dataclasses import dataclass

from modules.options.domain.enums import (
    OptionType,
    BillingType
)

@dataclass
class Option:

    id: str

    name: str

    type: OptionType

    price: float

    billing_type: BillingType = BillingType.FIXED

    is_active: bool = True