from enum import Enum

class VehicleType(str, Enum):
    SALE = "sale"
    RENT = "rent"

class EngineType(str, Enum):
    DIESEL = "diesel"
    PETROL = "petrol"
    HYBRID = "hybride"
    ELECTRIC = "electric"


class VehicleCondition(str, Enum):
    NEW = "new"
    USED = "used"

class VehicleOptionType(str, Enum):
    INCLUDED = "included"
    OPTIONAL = "optional"

class VehicleStatus(str, Enum):
    DRAFT = "DRAFT"
    AVAILABLE = "AVAILABLE"
    INSPECTION_PENDING = "INSPECTION_PENDING"
    INSPECTED = "INSPECTED"
    RECONDITIONING = "RECONDITIONING"
    RECONDITIONED = "RECONDITIONED"
    READY = "READY"
    PUBLISHED = "PUBLISHED"
    RESERVED = "RESERVED"
    SOLD = "SOLD"
    ARCHIVED = "ARCHIVED"