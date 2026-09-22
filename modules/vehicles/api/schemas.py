from typing import Literal, Optional, List
from datetime import datetime
from pydantic import BaseModel, field_validator, model_validator, Field
from modules.vehicles.domain.enums import VehicleType, VehicleCondition, EngineType, VehicleStatus
from modules.warranties.api.schemas import WarrantyPlanResponse
from modules.options.domain.enums import OptionType
from modules.inspections.api.schemas import InspectionResponse
from modules.reconditionings.api.schemas import ReconditioningResponse
from pydantic import BaseModel
from typing import Literal
import re



# =========================
# COMMON - VEHICLE RESPONSE
# =========================
class VehicleImageResponse(BaseModel):
    key: str
    url: str

class OptionResponse(BaseModel):

    id: str
    name: str
    type: OptionType
    price: float
    billing_type: str
    is_active: bool

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

class VehicleResponse(BaseModel):
    id: str
    brand: str
    model: str
    price: float
    type: VehicleType
    mileage: int
    year: int

    description: str | None = None
    engine_type: EngineType | None = None

    equipments: list[str] = Field(default_factory=list)
    condition: VehicleCondition

    is_available: bool
    images: list[VehicleImageResponse] = []
    status: VehicleStatus

    published_at: datetime | None = None
    final_check_at: datetime | None = None

    # 🚗 NEW FIELD
    license_plate: Optional[str] = Field(
        default=None,
        pattern=r"^[A-Z]{2}-\d{3}-[A-Z]{2}$"
    )

    included_options: list[OptionResponse] = Field(default_factory=list)
    optional_options: list[OptionResponse] = Field(default_factory=list)
    warranty_plan: WarrantyPlanResponse | None = None

# =========================
# COMMON - VEHICLE ACTION RESPONSE
# =========================
class VehicleActionResponse(BaseModel):
    vehicle_id: str
    status: str
    message: str

# =========================
# ADMIN - CREATE VEHICLE
# =========================
class CreateVehicleRequest(BaseModel):

    brand: str
    model: str
    price: float

    type: VehicleType

    mileage: int
    year: int

    description: str | None = None

    engine_type: EngineType

    equipments: list[str] = []

    condition: VehicleCondition

    images: list[str] = []

    license_plate: str | None = None

    warranty_plan_id: str | None = None

    included_options: list[str] = []

    optional_options: list[str] = []

    # =========================
    # VALIDATORS
    # =========================
    @field_validator("license_plate")
    @classmethod
    def validate_license_plate(cls, value):
        if not value:
            raise ValueError("Le champ immatriculation est obligatoire")

        value = value.upper().replace(" ", "")

        pattern = r"^[A-Z]{2}-\d{3}-[A-Z]{2}$"

        if not re.match(pattern, value):
            raise ValueError(
                "Format d'immatriculation invalide (ex: AB-123-CD)"
            )

        return value

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("Le prix doit être supérieur à 0")

        if v > 1_000_000:
            raise ValueError("Le prix est trop élevé")

        return v

    @field_validator("mileage")
    @classmethod
    def validate_mileage(cls, v):
        if v < 0:
            raise ValueError("Le kilométrage ne peut pas être négatif")

        if v > 500_000:
            raise ValueError("Le kilométrage est trop élevé")

        return v

    @field_validator("year")
    @classmethod
    def validate_year(cls, v):
        current_year = datetime.now().year

        if v < 1900:
            raise ValueError("L'année est trop ancienne")

        if v > current_year + 1:
            raise ValueError("L'année ne peut pas être dans le futur")

        return v

    # =========================
    # GLOBAL VALIDATION
    # =========================

    @model_validator(mode="after")
    def validate_consistency(self):

        if self.condition == VehicleCondition.NEW and self.mileage > 100:
            raise ValueError("Un véhicule neuf ne peut pas avoir autant de kilomètres")

        if self.condition == VehicleCondition.USED and self.mileage == 0:
            raise ValueError("Un véhicule d'occasion ne peut pas avoir 0 km")

        if self.year < 2005 and self.price > 50_000:
            raise ValueError("Le prix est trop élevé pour un véhicule ancien")

        return self

# =========================
# ADMIN - DELETE VEHICLE
# =========================
class DeleteVehicleResponse(BaseModel):

    vehicle_id: str

    action: Literal[
        "ARCHIVED",
        "DELETED",
    ]

    message: str

# =========================
# ADMIN - UPDATE VEHICLE
# =========================
class UpdateVehicleRequest(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    price: Optional[float] = None
    type: Optional[VehicleType] = None

    mileage: Optional[int] = None  # obligatoire métier mais optionnel PATCH
    year: Optional[int] = None

    description: Optional[str] = None  # autorisé vide
    engine_type: Optional[EngineType] = None

    equipments: Optional[List[str]] = None  # peut être vide
    condition: Optional[VehicleCondition] = None

    images: Optional[List[str]] = None

    # 🚗 IMMATRICULATION
    license_plate: Optional[str] = None

    # 🛡️ GARANTIE (OPTIONNEL)
    warranty_plan_id: Optional[str] = None

    included_options: Optional[List[str]] = None
    optional_options: Optional[List[str]] = None

    # =========================
    # IMMATRICULATION VALIDATION
    # =========================
    @field_validator("license_plate")
    @classmethod
    def validate_plate(cls, value):
        if value is None:
            return None

        value = value.upper().replace(" ", "")

        if not re.match(r"^[A-Z]{2}-\d{3}-[A-Z]{2}$", value):
            raise ValueError("Format d'immatriculation invalide (ex : AB-123-CD)")

        return value

    # =========================
    # PRIX
    # =========================
    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        if v is None:
            return v

        if v <= 0:
            raise ValueError("Le prix doit être supérieur à 0")

        if v > 1_000_000:
            raise ValueError("Le prix est trop élevé")

        return v

    # =========================
    # KILOMÉTRAGE
    # =========================
    @field_validator("mileage")
    @classmethod
    def validate_mileage(cls, v):
        if v is None:
            return v

        if v < 0:
            raise ValueError("Le kilométrage ne peut pas être négatif")

        if v > 500_000:
            raise ValueError("Le kilométrage est trop élevé")

        return v

    # =========================
    # ANNÉE
    # =========================
    @field_validator("year")
    @classmethod
    def validate_year(cls, v):
        if v is None:
            return v

        current_year = datetime.now().year

        if v < 1900:
            raise ValueError("L'année est trop ancienne")

        if v > current_year + 1:
            raise ValueError("L'année ne peut pas être dans le futur")

        return v

    # =========================
    # DESCRIPTION CLEAN
    # =========================
    @field_validator("description")
    @classmethod
    def clean_description(cls, v):
        if v is None:
            return v
        return v.strip()

    # =========================
    # COHÉRENCE GLOBALE
    # =========================
    @field_validator("mileage", "condition")
    @classmethod
    def validate_condition_logic(cls, v, info):
        values = info.data

        mileage = values.get("mileage")
        condition = values.get("condition")

        if mileage is not None and condition is not None:

            if condition == VehicleCondition.NEW and mileage > 100:
                raise ValueError("Un véhicule neuf ne peut pas avoir autant de kilomètres")

            if condition == VehicleCondition.USED and mileage == 0:
                raise ValueError("Un véhicule d'occasion ne peut pas avoir 0 km")

        return v


# =========================
# ADMIN - GET VEHICLE LIFECYCLE
# =========================

class VehicleLifecycleResponse(BaseModel):
    inspection: Optional[InspectionResponse] = None
    reconditioning: Optional[ReconditioningResponse] = None

# =========================
# ADMIN - FINAL CHECK
# =========================
class FinalCheckResponse(BaseModel):

    vehicle_id: str

    vehicle_status: str

    reconditioning_status: str

    final_check_at: datetime

# =========================
# ADMIN - SET VEHICLE AVAILABILITY
# =========================
class SetAvailabilityRequest(BaseModel):
    value: bool

# =========================
# SHARED - GET VEHICLES
# =========================
class VehicleSearchFilters(BaseModel):
    page: int = 1
    size: int = 10

    sort_by: Literal["price", "year", "mileage"] = "year"
    order: Literal["asc", "desc"] = "desc"

    search: Optional[str] = None

    type: Optional[VehicleType] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    engine_type: Optional[EngineType] = None

    price_min: Optional[float] = None
    price_max: Optional[float] = None

    year_min: Optional[int] = None
    mileage_max: Optional[int] = None

    is_available: Optional[bool] = None

    # 🚗 SEARCH IMMATRICULATION (FLEXIBLE)
    license_plate: Optional[str] = None

    # =========================
    # NORMALISATION PLAQUE
    # =========================
    @field_validator("license_plate")
    @classmethod
    def normalize_plate(cls, value):
        if not value:
            return None

        value = value.upper().replace(" ", "")

        return value



# =========================
# ADMIN - GET VEHICLES
# =========================
class VehicleAdminSearchFilters(BaseModel):

    page: int = Field(
        default=1,
        ge=1
    )

    size: int = Field(
        default=10,
        ge=1,
        le=100
    )

    search: str | None = None

    license_plate: str | None = None

    type: VehicleType | None = None



# =========================
# CLIENT - GET VEHICLES
# =========================
class VehicleSearchFilters(BaseModel):

    # =========================
    # PAGINATION
    # =========================

    page: int = Field(
        default=1,
        ge=1,
    )

    size: int = Field(
        default=10,
        ge=1,
        le=100,
    )

    # =========================
    # TRI
    # =========================

    sort_by: Literal[
        "price",
        "year",
        "mileage",
    ] = "year"

    order: Literal[
        "asc",
        "desc",
    ] = "desc"

    # =========================
    # FILTRES
    # =========================

    brand: str | None = None

    model: str | None = None

    type: VehicleType | None = None

    engine_type: EngineType | None = None

    price_min: float | None = Field(
        default=None,
        ge=0,
    )

    price_max: float | None = Field(
        default=None,
        ge=0,
    )

    year_min: int | None = Field(
        default=None,
        ge=1900,
    )

    mileage_max: int | None = Field(
        default=None,
        ge=0,
    )

# =========================
# CLIENT - GET VEHICLE INTEREST STATUS
# =========================

class VehicleInterestStatusResponse(BaseModel):

    already_interested: bool

    quote_id: str | None = None

    quote_status: str | None = None

    application_id: str | None = None

# =========================
# CLIENT - GET VEHICLE AVAILABILITY
# =========================
class UnavailableDateResponse(BaseModel):
    start: datetime
    end: datetime