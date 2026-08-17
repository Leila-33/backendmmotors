from pydantic import BaseModel, Field, field_validator

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

    price: float = Field(
        gt=0
    )

    billing_type: BillingType = (
            BillingType.FIXED
        )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):

        value = value.strip()

        if not value:
            raise ValueError(
                "Le nom de l'option est obligatoire"
            )

        return value

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


class ToggleOptionStatusResponse(BaseModel):

    id: str
    is_active: bool
    message: str

# =========================
# RESPONSE
# =========================
class OptionResponse(BaseModel):

    id: str
    name: str
    type: OptionType
    price: float
    billing_type: str
    is_active: bool


class GetOptionsResponse(BaseModel):

    options: list[OptionResponse] = Field(
        default_factory=list
    )