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
    # USERS
    # =========================
    USER_REGISTERED = "user_registered"
    USER_EMAIL_VERIFIED = "user_email_verified"
    USER_ACTIVATED = "user_activated"
    USER_DEACTIVATED = "user_deactivated"
    USER_CREATED = "user_created"
    USER_ARCHIVED = "user_archived"
    USER_UNARCHIVED = "user_unarchived"
    USER_ROLE_UPDATED = "user_role_updated"
    USER_ACCOUNT_ACTIVATED ="user_account_activated"

    # =========================
    # LEADS
    # =========================
    LEAD_CREATED = "lead_created"
    LEAD_ASSIGNED = "lead_assigned"
    LEAD_CONTACTED = "lead_contacted"
    LEAD_WON = "lead_won"
    LEAD_DELETED = "lead_deleted"

    # =========================
    # QUOTES
    # =========================
    QUOTE_CREATED = "quote_created"
    QUOTE_UPDATED = "quote_updated"
    QUOTE_SENT = "quote_sent"
    QUOTE_ACCEPTED = "quote_accepted"
    QUOTE_REFUSED = "quote_refused"
    QUOTE_DELETED = "quote_deleted"
    QUOTE_EXPIRED = "quote_expired"

    # =========================
    # OPTIONS
    # =========================

    OPTION_CREATED = "option_created"

    OPTION_UPDATED = "option_updated"

    OPTION_ACTIVATED = "option_activated"

    OPTION_DEACTIVATED = "option_deactivated"

    # =========================
    # APPLICATIONS
    # =========================
    APPLICATION_CREATED = "application_created"
    APPLICATION_SUBMITTED = "application_submitted"
    APPLICATION_APPROVED = "application_approved"
    APPLICATION_REJECTED = "application_rejected"

    APPLICATION_ARCHIVED = "application_archived"
    APPLICATION_UNARCHIVED = "application_unarchived"
    APPLICATION_RESTORED = "application_restored"
    APPLICATION_CANCELLED = "application_cancelled"
    APPLICATION_SOFT_DELETED = "application_soft_deleted"

    APPLICATION_STATUS_UPDATED = "application_status_updated"

    # =========================
    # DOCUMENTS
    # =========================
    DOCUMENT_VALIDATED = "document_validated"
    DOCUMENT_REJECTED = "document_rejected"

    # =========================
    # VEHICLES
    # =========================
    VEHICLE_CREATED = "vehicle_created"
    VEHICLE_UPDATED = "vehicle_updated"
    VEHICLE_DELETED = "vehicle_deleted"
    VEHICLE_ARCHIVED = "vehicle_archived"

    VEHICLE_PUBLISHED = "vehicle_published"
    VEHICLE_UNPUBLISHED = "vehicle_unpublished"

    VEHICLE_AVAILABILITY_CHANGED = (
        "vehicle_availability_changed"
    )

    # =========================
    # INSPECTION
    # =========================
    INSPECTION_STARTED = "inspection_started"
    INSPECTION_COMPLETED = "inspection_completed"

    # =========================
    # RECONDITIONING
    # =========================
    RECONDITIONING_STARTED = "reconditioning_started"
    RECONDITIONING_COMPLETED = "reconditioning_completed"

    # =========================
    # FINAL CHECK
    # =========================
    FINAL_CHECK_COMPLETED = "final_check_completed"

    # =========================
    # PAYMENTS
    # =========================
    PAYMENT_INITIATED = "payment_initiated"
    PAYMENT_SUCCEEDED = "payment_succeeded"
    PAYMENT_FAILED = "payment_failed"
    DEPOSIT_PAID = "deposit_paid"

    # =========================
    # FINANCING
    # =========================
    FINANCING_CONTRACT_CREATED = (
        "financing_contract_created"
    )

    FINANCING_COMPLETED = (
        "financing_completed"
    )

    # =========================
    # SUBSCRIPTIONS
    # =========================
    SUBSCRIPTION_CREATED = "subscription_created"

    # =========================
    # INSTALLMENTS
    # =========================
    INSTALLMENT_PAID = "installment_paid"
    INSTALLMENT_FAILED = "installment_failed"

    # =========================
    # RENTALS
    # =========================
    RENTAL_CREATED = "rental_created"
    RENTAL_PAYMENT_PAID = "rental_payment_paid"
    RENTAL_COMPLETED = "rental_completed"
    RENTAL_CANCELLED = "rental_cancelled"

    # =========================
    # TEST DRIVES
    # =========================
    TEST_DRIVE_CREATED = "test_drive_created"
    TEST_DRIVE_CONFIRMED = "test_drive_confirmed"
    TEST_DRIVE_REJECTED = "test_drive_rejected"
    TEST_DRIVE_CANCELLED = "test_drive_cancelled"
    TEST_DRIVE_COMPLETED = "test_drive_completed"

    # =========================
    # WARRANTIES
    # =========================
    WARRANTY_PLAN_CREATED = "warranty_plan_created"
    WARRANTY_PLAN_UPDATED = "warranty_plan_updated"
    WARRANTY_PLAN_ACTIVATED = "warranty_plan_activated"
    WARRANTY_PLAN_DEACTIVATED = "warranty_plan_deactivated"

    WARRANTY_ACTIVATED = "warranty_activated"

    # =========================
    # SUPPORT / SAV
    # =========================
    SUPPORT_TICKET_CREATED = "support_ticket_created"
    SUPPORT_TICKET_ARCHIVED = "support_ticket_archived"
    SUPPORT_TICKET_STATUS_CHANGED = (
        "support_ticket_status_changed"
    )

    # =========================
    # ADMIN
    # =========================
    ADMIN_ACTION = "admin_action"


class ViewMode(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"