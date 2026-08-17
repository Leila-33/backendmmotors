from dataclasses import dataclass

from modules.options.domain.enums import BillingType


@dataclass
class CreateOptionDTO:

    name: str
    price: float
    billing_type: BillingType = (
            BillingType.FIXED
        )