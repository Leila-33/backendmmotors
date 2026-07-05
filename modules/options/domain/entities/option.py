from dataclasses import dataclass
from typing import Optional

from modules.core.enums import OptionType, BillingType

@dataclass
class Option:

    id: str

    name: str

    type: OptionType

    price: Optional[float] = None

    billing_type: BillingType = BillingType.fixed

    is_active: bool = True