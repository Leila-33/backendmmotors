from pydantic import BaseModel, Field

from modules.options.domain.enums import BillingType


class UpdateOptionDTO(BaseModel):

    option_id: str

    name: str = Field(
        min_length=1,
        max_length=100,
    )

    price: float = Field(
        gt=0,
    )

    billing_type: BillingType

    admin_id: str