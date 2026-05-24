from pydantic import BaseModel
from typing import Optional

from modules.core.enums import OptionType

# =========================
# CREATE
# =========================
class CreateOptionRequest(BaseModel):
    name: str
    type: OptionType
    price: Optional[float] = None


# =========================
# UPDATE
# =========================
class UpdateOptionRequest(BaseModel):
    name: Optional[str] = None
    type: Optional[OptionType] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None


# =========================
# RESPONSE
# =========================
class OptionResponse(BaseModel):
    id: str
    name: str
    type: OptionType
    price: Optional[float] = None
    is_active: bool