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
    DRAFT = "draft"
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




from enum import Enum

class ApplicationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

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
    SAV_AGENT = "sav_agent"
    COMMERCIAL_AGENT = "commercial_agent"


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
    # APPLICATION LIFECYCLE
    # =========================
    APPLICATION_CREATED = "application_created"
    APPLICATION_SUBMITTED = "application_submitted"
    APPLICATION_APPROVED = "application_approved"
    APPLICATION_REJECTED = "application_rejected"

    APPLICATION_ARCHIVED = "application_archived"
    APPLICATION_RESTORED = "application_restored"
    APPLICATION_CANCELLED = "application_cancelled"

    # =========================
    # DOCUMENTS
    # =========================
    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_VALIDATED = "document_validated"
    DOCUMENT_REJECTED = "document_rejected"

    # =========================
    # PAYMENTS (ACOMPTE)
    # =========================
    PAYMENT_INITIATED = "payment_initiated"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"

    DEPOSIT_PAID = "deposit_paid"

    # =========================
    # FINANCING
    # =========================
    FINANCING_CONTRACT_CREATED = "financing_contract_created"

    FINANCING_COMPLETED = (
        "financing_completed"
    )

    # =========================
    # RENTAL
    # =========================
    RENTAL_PAYMENT_PAID = "rental_payment_paid"
    RENTAL_COMPLETED = "rental_completed"

    # =========================
    # SUBSCRIPTION (STRIPE)
    # =========================
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_ACTIVE = "subscription_active"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"

    # =========================
    # INSTALLMENTS
    # =========================
    INSTALLMENT_PAID = "installment_paid"
    INSTALLMENT_FAILED = "installment_failed"
    INSTALLMENT_OVERDUE = "installment_overdue"

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


    # WARRANTY
    WARRANTY_CREATED = "warranty_created"
    WARRANTY_ACTIVATED = "warranty_activated"
    WARRANTY_EXPIRED = "warranty_expired"



# =========================
# TEST_DRIVE
# =========================

class TestDriveStatus(str, Enum):

    PENDING = "pending"

    CONFIRMED = "confirmed"
    REJECTED = "rejected"

    CANCELLED = "cancelled"

    COMPLETED = "completed"



class WarrantyPlanType(str, Enum):
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    CUSTOM = "custom"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class BillingType(str, Enum):
    fixed = "fixed"
    daily = "daily"

class InstallmentStatus(Enum):

    PENDING = "PENDING"

    PAID = "PAID"

    FAILED = "FAILED"

    LATE = "LATE"


class SubscriptionStatus(str, Enum):

    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class ViewMode(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"

class InspectionStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class VehicleStatus(str, Enum):
    DRAFT = "DRAFT"
    AVAILABLE = "AVAILABLE"
    INSPECTION_PENDING = "INSPECTION_PENDING"
    INSPECTED = "INSPECTED"
    RECONDITIONING = "RECONDITIONING"
    READY = "READY"
    PUBLISHED = "PUBLISHED"
    RESERVED = "RESERVED"
    SOLD = "SOLD"

class ReconditioningStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    APPROVED = "APPROVED"


class TicketStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_CUSTOMER = "WAITING_CUSTOMER"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"



class TicketPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"



class TicketCategory(str, Enum):
    GENERAL = "GENERAL"
    FINANCING = "FINANCING"
    DELIVERY = "DELIVERY"
    WARRANTY = "WARRANTY"
    VEHICLE_ISSUE = "VEHICLE_ISSUE"
    DOCUMENTS = "DOCUMENTS"
    PAYMENT = "PAYMENT"
    OTHER = "OTHER"


class TicketFilter(str, Enum):
    ALL = "all"
    OPEN = "open"
    URGENT = "urgent"
