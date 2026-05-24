from pydantic import BaseModel, Field, field_validator, ValidationInfo
from datetime import datetime

from modules.core.enums import TradeInVehicleCondition


class TradeInEstimateRequest(BaseModel):

    brand: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)

    year: int
    mileage: int

    condition: TradeInVehicleCondition

    # =========================
    # VALIDATION YEAR
    # =========================
    @field_validator("year")
    @classmethod
    def validate_year(cls, v):
        current_year = datetime.now().year

        if v < 1900:
            raise ValueError("Année invalide (min 1900)")

        if v > current_year:
            raise ValueError("Année ne peut pas être dans le futur")

        return v

    # =========================
    # VALIDATION MILEAGE
    # =========================
    @field_validator("mileage")
    @classmethod
    def validate_mileage(cls, v):
        if v < 0:
            raise ValueError("Kilométrage doit être positif")

        if v > 1_000_000:
            raise ValueError("Kilométrage incohérent")

        return v
    





class FinancingRequest(BaseModel):

    total_price: float = Field(..., ge=0)
    down_payment: float = Field(0, ge=0)
    duration_months: int = Field(..., ge=1, le=120)

    trade_in_value: float = Field(0, ge=0)

    # =========================
    # VALIDATION COHERENCE
    # =========================
    @field_validator("down_payment")
    @classmethod
    def validate_down_payment(cls, v, info: ValidationInfo):

        total_price = info.data.get("total_price", 0)

        if v > total_price:
            raise ValueError("L'apport ne peut pas dépasser le prix total")

        return v

    @field_validator("trade_in_value")
    @classmethod
    def validate_trade_in(cls, v, info):

        total_price = info.data.get("total_price", 0)

        if v > total_price:
            raise ValueError("La reprise ne peut pas dépasser le prix du véhicule")

        return v
    


class FinancingResponse(BaseModel):

    financed_amount: float = Field(...)
    monthly_payment: float = Field(...)