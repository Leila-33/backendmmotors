from pydantic import BaseModel, Field, field_validator
from typing import Optional
from modules.warranties.domain.enums import WarrantyPlanType


# =====================================================
# DTO
# =====================================================

class WarrantyPlanPayload(BaseModel):

    # =========================
    # INFOS
    # =========================
    name: str = Field(..., min_length=2, max_length=120)

    description: Optional[str] = None

    plan_type: WarrantyPlanType

    # =========================
    # LIMITS
    # =========================
    duration_months: int

    mileage_limit: Optional[int] = None

    # =========================
    # COVERAGE
    # =========================
    covers_engine: bool = True

    covers_transmission: bool = True

    covers_electronics: bool = False

    covers_assistance: bool = False

    covers_wear_parts: bool = False

    # =========================
    # FINANCIAL
    # =========================
    price: float

    # =====================================================
    # VALIDATORS
    # =====================================================

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):

        value = value.strip()

        if not value:
            raise ValueError(
                "Le nom du plan est requis"
            )

        return value

    @field_validator("duration_months")
    @classmethod
    def validate_duration(cls, value):

        if value <= 0:
            raise ValueError(
                "La durée doit être supérieure à 0"
            )

        if value > 120:
            raise ValueError(
                "La durée maximale est de 120 mois"
            )

        return value

    @field_validator("mileage_limit")
    @classmethod
    def validate_mileage(cls, value):

        if value is not None and value < 0:
            raise ValueError(
                "Le kilométrage ne peut pas être négatif"
            )

        return value

    @field_validator("price")
    @classmethod
    def validate_price(cls, value):

        if value <= 0:
            raise ValueError(
                "Le prix doit être supérieur à 0"
            )

        return value

# =====================================================
# CREATE
# =====================================================
class CreateWarrantyPlanRequest(WarrantyPlanPayload):
    pass


class CreateWarrantyPlanResponse(BaseModel):

    id: str

    message: str

# =====================================================
# TOGGLE
# =====================================================

class ToggleWarrantyPlanRequest(BaseModel):

    active: bool


class UpdateWarrantyPlanResponse(BaseModel):

    id: str

    message: str


# =====================================================
# UPDATE
# =====================================================
class UpdateWarrantyPlanRequest(WarrantyPlanPayload):
    pass

# =====================================================
# WARRANTY PLAN RESPONSE
# =====================================================
class WarrantyPlanResponse(BaseModel):

    id: str

    name: str

    description: Optional[str]

    plan_type: str

    duration_months: int

    mileage_limit: Optional[int]

    covers_engine: bool

    covers_transmission: bool

    covers_electronics: bool

    covers_assistance: bool

    covers_wear_parts: bool

    price: float

    active: bool


    class Config:
        from_attributes = True