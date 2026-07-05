from pydantic import BaseModel, Field, field_validator
from typing import Optional

from modules.core.enums import WarrantyPlanType


# =====================================================
# DTO
# =====================================================

class CreateWarrantyPlanDTO(BaseModel):

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
    deductible: float = 0.0

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

    @field_validator("deductible")
    @classmethod
    def validate_deductible(cls, value):

        if value < 0:
            raise ValueError(
                "La franchise ne peut pas être négative"
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
# RESPONSE DTO
# =====================================================

class CreateWarrantyPlanResponseDTO(BaseModel):

    id: str

    name: str

    price: float

    active: bool

class ToggleWarrantyDTO(BaseModel):
    active: bool
