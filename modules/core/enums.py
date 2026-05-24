from enum import Enum


# =========================
# VEHICLE
# =========================

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


# =========================
# RESERVATION
# =========================
class ReservationStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


# =========================
# APPLICATION
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
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"

class ApplicationDecision(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    
class OptionUsageType(str, Enum):
    INCLUDED = "included"
    OPTIONAL = "optional"


# =========================
# OPTION
# =========================
class OptionType(str, Enum):
    ASSURANCE = "assurance_tous_risques"
    ASSISTANCE = "assistance_depannage"
    ENTRETIEN = "entretien_sav"
    CONTROLE_TECHNIQUE = "controle_technique"
    CUSTOM = "custom"


# =========================
# VEHICLE
# =========================
class VehicleOptionType(str, Enum):
    INCLUDED = "included"
    OPTIONAL = "optional"



# =========================
# NOTIFICATION
# =========================
class NotificationType(str, Enum):
    APPLICATION_APPROVED = "application_approved"

    APPLICATION_REJECTED = "application_rejected"

    APPLICATION_SUBMITTED = "application_submitted"

    DOCUMENT_REJECTED = "document_rejected"
    TEST_DRIVE_CONFIRMED = "test_drive_confirmed"

    TEST_DRIVE_CANCELLED = "test_drive_cancelled"

    TEST_DRIVE_REJECTED = "test_drive_rejected"

    TEST_DRIVE_COMPLETED = "test_drive_completed"


class NotificationStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"

# =========================
# USER
# =========================
class UserRole(str, Enum):
    ADMIN = "admin"
    CLIENT = "client"


# =========================
# TRADEIN
# =========================
class TradeInVehicleCondition(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"




# =========================
# EVENT
# =========================

from enum import Enum


class EventType(str, Enum):

    # =========================
    # APPLICATION
    # =========================

    APPLICATION_CREATED = "application_created"
    APPLICATION_SUBMITTED = "application_submitted"
    APPLICATION_APPROVED = "application_approved"
    APPLICATION_REJECTED = "application_rejected"

    APPLICATION_ARCHIVED = "application_archived"
    APPLICATION_RESTORED = "application_restored"

    # =========================
    # DOCUMENTS
    # =========================

    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_VALIDATED = "document_validated"
    DOCUMENT_REJECTED = "document_rejected"

    # =========================
    # TEST DRIVE
    # =========================

    TEST_DRIVE_CREATED = "test_drive_created"
    TEST_DRIVE_CONFIRMED = "test_drive_confirmed"
    TEST_DRIVE_REJECTED = "test_drive_rejected"
    TEST_DRIVE_CANCELLED = "test_drive_cancelled"
    TEST_DRIVE_COMPLETED = "test_drive_completed"

    # =========================
    # NOTIFICATION SYSTEM
    # =========================

    NOTIFICATION_SENT = "notification_sent"

    # =========================
    # ADMIN ACTIONS
    # =========================

    ADMIN_ACTION = "admin_action"




# =========================
# TEST_DRIVE
# =========================

class TestDriveStatus(str, Enum):

    PENDING = "pending"

    CONFIRMED = "confirmed"
    REJECTED = "rejected"

    CANCELLED = "cancelled"

    COMPLETED = "completed"