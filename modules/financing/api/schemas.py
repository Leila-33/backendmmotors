from pydantic import BaseModel, Field


# ============================================================
# ESTIMATE TRADE IN
# ============================================================
class TradeInEstimateRequest(BaseModel):
    brand: str
    model: str
    year: int
    mileage: int
    condition: str

class TradeInEstimateResponse(BaseModel):

    estimated_value: float