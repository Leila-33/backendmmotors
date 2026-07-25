from pydantic import BaseModel, Field
from typing import Optional

from modules.options.domain.enums import (
    OptionType,
    BillingType
)

# =========================
# CREATE
# =========================
class CreateOptionRequest(BaseModel):

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    price: float | None = Field(
        default=None,
        ge=0,
    )

    billing_type: BillingType = (
        BillingType.FIXED
    )



class CreateOptionResponse(BaseModel):

    id: str

    message: str

# =========================
# UPDATE
# =========================
class UpdateOptionRequest(BaseModel):

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    price: float | None = Field(
        default=None,
        ge=0,
    )

    billing_type: BillingType = (
        BillingType.FIXED
    )    

class UpdateOptionResponse(BaseModel):

    id: str

    message: str


# =========================
# UPDATE
# =========================
class ToggleOptionStatusRequest(BaseModel):

    is_active: bool

# =========================
# RESPONSE
# =========================
class OptionResponse(BaseModel):
    id: str
    name: str
    type: OptionType
    price: float
    is_active: bool
    billing_type : BillingType