from pydantic import BaseModel, Field, HttpUrl, field_validator
from enum import Enum
from typing import Optional


# =========================
# ENUMS
# =========================

class DocumentType(str, Enum):
    IDENTITY = "identity"
    RIB = "rib"
    PAYSLIP = "payslip"
    ADDRESS_PROOF = "address_proof"


class DocumentStatus(str, Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"


class ApplicationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


# =========================
# REQUESTS
# =========================

class CreateApplicationRequest(BaseModel):
    vehicle_id: str

    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    employment_status: Optional[str] = None


class UpdateApplicationRequest(BaseModel):
    monthly_income: Optional[float] = Field(None, gt=0)
    monthly_expenses: Optional[float] = Field(None, ge=0)
    employment_status: Optional[str] = Field(None, min_length=2, max_length=50)


class SubmitApplicationRequest(BaseModel):
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    employment_status: Optional[str] = None


class SubmitNewApplicationRequest(BaseModel):
    vehicle_id: str

    monthly_income: float = Field(..., gt=0)
    monthly_expenses: float = Field(..., ge=0)
    employment_status: str = Field(..., min_length=2, max_length=50)


# 🔹 Upload sur application existante
class UploadDocumentRequest(BaseModel):
    type: DocumentType
    file_url: HttpUrl

    @field_validator("file_url")
    def validate_extension(cls, v):
        if not str(v).lower().endswith((".pdf", ".jpg", ".png")):
            raise ValueError("Format autorisé : PDF, JPG, PNG")
        return v


# 🔹 Upload + création draft
class UploadDocumentWithDraftRequest(BaseModel):
    vehicle_id: str
    type: DocumentType
    file_url: HttpUrl

    @field_validator("file_url")
    def validate_extension(cls, v):
        if not str(v).lower().endswith((".pdf", ".jpg", ".png")):
            raise ValueError("Format autorisé : PDF, JPG, PNG")
        return v


# =========================
# RESPONSES
# =========================

class ApplicationResponse(BaseModel):
    id: str
    status: ApplicationStatus
    message: Optional[str] = None


class DocumentResponse(BaseModel):
    id: str
    application_id: str
    type: DocumentType
    file_url: HttpUrl
    status: DocumentStatus
    comment: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


    # =========================
# 🔥 US5 – STATUS RESPONSE
# =========================
class VehicleInfo(BaseModel):
    brand: str
    model: str


class ProjectInfo(BaseModel):
    type: str
    vehicle: VehicleInfo


class ApplicationStatusResponse(BaseModel):
    id: str
    status: str
    createdAt: str
    submittedAt: Optional[str]
    project: ProjectInfo