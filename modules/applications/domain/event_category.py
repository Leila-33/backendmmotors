from modules.applications.domain.enums import (
    EventType,
    EventCategory
)


EVENT_CATEGORIES = {

    # =====================================================
    # UTILISATEURS
    # =====================================================

    EventCategory.USER: [
        EventType.USER_REGISTERED,
        EventType.USER_EMAIL_VERIFIED,
        EventType.USER_ACTIVATED,
        EventType.USER_DEACTIVATED,
        EventType.USER_CREATED,
        EventType.USER_ARCHIVED,
        EventType.USER_UNARCHIVED,
        EventType.USER_ROLE_UPDATED,
        EventType.USER_ACCOUNT_ACTIVATED,
    ],

    # =====================================================
    # LEADS
    # =====================================================

    EventCategory.LEAD: [
        EventType.LEAD_CREATED,
        EventType.LEAD_ASSIGNED,
        EventType.LEAD_CONTACTED,
        EventType.LEAD_WON,
        EventType.LEAD_DELETED,
    ],

    # =====================================================
    # OFFRES
    # =====================================================

    EventCategory.QUOTE: [
        EventType.QUOTE_CREATED,
        EventType.QUOTE_UPDATED,
        EventType.QUOTE_SENT,
        EventType.QUOTE_ACCEPTED,
        EventType.QUOTE_REFUSED,
        EventType.QUOTE_DELETED,
        EventType.QUOTE_EXPIRED,
    ],

    # =====================================================
    # OPTIONS
    # =====================================================

    EventCategory.OPTION: [
        EventType.OPTION_CREATED,
        EventType.OPTION_UPDATED,
        EventType.OPTION_ACTIVATED,
        EventType.OPTION_DEACTIVATED,
    ],

    # =====================================================
    # DOSSIERS
    # =====================================================

    EventCategory.APPLICATION: [
        EventType.APPLICATION_CREATED,
        EventType.APPLICATION_SUBMITTED,
        EventType.APPLICATION_PROCESSING,
        EventType.APPLICATION_APPROVED,
        EventType.APPLICATION_REJECTED,
        EventType.APPLICATION_ARCHIVED,
        EventType.APPLICATION_UNARCHIVED,
        EventType.APPLICATION_RESTORED,
        EventType.APPLICATION_CANCELLED,
        EventType.APPLICATION_SOFT_DELETED,
        EventType.APPLICATION_STATUS_UPDATED,
    ],

    # =====================================================
    # DOCUMENTS
    # =====================================================

    EventCategory.DOCUMENT: [
        EventType.DOCUMENT_VALIDATED,
        EventType.DOCUMENT_REJECTED,
    ],

    # =====================================================
    # VÉHICULES
    # =====================================================

    EventCategory.VEHICLE: [
        EventType.VEHICLE_CREATED,
        EventType.VEHICLE_UPDATED,
        EventType.VEHICLE_DELETED,
        EventType.VEHICLE_ARCHIVED,
        EventType.VEHICLE_PUBLISHED,
        EventType.VEHICLE_UNPUBLISHED,
        EventType.VEHICLE_AVAILABILITY_CHANGED,
    ],

    # =====================================================
    # INSPECTION
    # =====================================================

    EventCategory.INSPECTION: [
        EventType.INSPECTION_STARTED,
        EventType.INSPECTION_COMPLETED,
    ],

    # =====================================================
    # RECONDITIONNEMENT
    # =====================================================

    EventCategory.RECONDITIONING: [
        EventType.RECONDITIONING_STARTED,
        EventType.RECONDITIONING_COMPLETED,
    ],

    # =====================================================
    # CONTRÔLE FINAL
    # =====================================================

    EventCategory.FINAL_CHECK: [
        EventType.FINAL_CHECK_COMPLETED,
    ],

    # =====================================================
    # PAIEMENTS
    # =====================================================

    EventCategory.PAYMENT: [
        EventType.PAYMENT_INITIATED,
        EventType.PAYMENT_SUCCEEDED,
        EventType.PAYMENT_FAILED,
        EventType.DEPOSIT_PAID,
    ],

    # =====================================================
    # FINANCEMENT
    # =====================================================

    EventCategory.FINANCING: [
        EventType.FINANCING_CONTRACT_CREATED,
        EventType.FINANCING_COMPLETED,
    ],

    # =====================================================
    # ABONNEMENTS
    # =====================================================

    EventCategory.SUBSCRIPTION: [
        EventType.SUBSCRIPTION_CREATED,
    ],

    # =====================================================
    # ÉCHÉANCES
    # =====================================================

    EventCategory.INSTALLMENT: [
        EventType.INSTALLMENT_PAID,
        EventType.INSTALLMENT_FAILED,
    ],

    # =====================================================
    # LOCATIONS
    # =====================================================

    EventCategory.RENTAL: [
        EventType.RENTAL_CREATED,
        EventType.RENTAL_PAYMENT_PAID,
        EventType.RENTAL_COMPLETED,
        EventType.RENTAL_CANCELLED,
    ],

    # =====================================================
    # ESSAIS
    # =====================================================

    EventCategory.TEST_DRIVE: [
        EventType.TEST_DRIVE_CREATED,
        EventType.TEST_DRIVE_CONFIRMED,
        EventType.TEST_DRIVE_REJECTED,
        EventType.TEST_DRIVE_CANCELLED,
        EventType.TEST_DRIVE_COMPLETED,
    ],

    # =====================================================
    # GARANTIES
    # =====================================================

    EventCategory.WARRANTY: [
        EventType.WARRANTY_PLAN_CREATED,
        EventType.WARRANTY_PLAN_UPDATED,
        EventType.WARRANTY_PLAN_ACTIVATED,
        EventType.WARRANTY_PLAN_DEACTIVATED,
        EventType.WARRANTY_ACTIVATED,
    ],

    # =====================================================
    # SAV
    # =====================================================

    EventCategory.SUPPORT_TICKET: [
        EventType.SUPPORT_TICKET_CREATED,
        EventType.SUPPORT_TICKET_ARCHIVED,
        EventType.SUPPORT_TICKET_STATUS_CHANGED,
    ],

    # =====================================================
    # ADMINISTRATION
    # =====================================================

    EventCategory.ADMIN: [
        EventType.ADMIN_ACTION,
    ],
}