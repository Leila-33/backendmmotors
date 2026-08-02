from enum import Enum

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
    PAID = "paid"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ApplicationType(str, Enum):
    SALE = "sale"
    RENT = "rent"

class OptionUsageType(str, Enum):
    INCLUDED = "included"
    OPTIONAL = "optional"

class TradeInVehicleCondition(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"

class EventType(str, Enum):

    # =========================
    # APPLICATION LIFECYCLE
    # =========================
    APPLICATION_CREATED = "application_created"
    APPLICATION_SUBMITTED = "application_submitted"
    APPLICATION_APPROVED = "application_approved"
    APPLICATION_REJECTED = "application_rejected"

    APPLICATION_ARCHIVED = "application_archived"
    APPLICATION_UNARCHIVED = "application_unarchived"
    APPLICATION_RESTORED = "application_restored"
    APPLICATION_CANCELLED = "application_cancelled"
    APPLICATION_DELETED = "application_deleted"

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
    RENTAL_CANCELLED = "rental_cancelled"

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

class ViewMode(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"