# modules/core/infrastructure/dependencies.py

from fastapi import Depends
from sqlalchemy.orm import Session

from core.database.dependencies import get_db

# =====================================================
# APPLICATIONS
# =====================================================

from modules.applications.domain.repositories.application_repository import (
    ApplicationRepository,
)

from modules.applications.infrastructure.repositories.application_repository_sql import (
    ApplicationRepositorySQL,
)
from modules.applications.infrastructure.repositories.document_repository_sql import (
    DocumentRepositorySQL,
)
from modules.applications.infrastructure.repositories.event_repository_sql import (
    EventRepositorySQL,
)
from modules.applications.infrastructure.repositories.application_trade_in_repository_sql import (
    ApplicationTradeInRepositorySQL,
)
from modules.applications.infrastructure.repositories.application_financing_repository_sql import (
    ApplicationFinancingRepositorySQL,
)
from modules.applications.infrastructure.repositories.application_option_repository_sql import (
    ApplicationOptionRepositorySQL,
)
from modules.applications.domain.repositories.document_repository import DocumentRepository
from modules.storage.api.dependencies import get_s3_service
from modules.applications.application.services.event_service import EventService

def get_application_repository(
    db: Session = Depends(get_db),
) -> ApplicationRepository:
    return ApplicationRepositorySQL(db)


def get_event_repository(
    db: Session = Depends(get_db),
):
    return EventRepositorySQL(db)

def get_event_service(
    event_repository = Depends(
        get_event_repository
    )
):

    return EventService(
        event_repository
    )

def get_document_repository(
    db: Session = Depends(get_db),
):
    return DocumentRepositorySQL(db)



def get_trade_in_repository(
    db: Session = Depends(get_db),
):
    return ApplicationTradeInRepositorySQL(db)


def get_financing_repository(
    db: Session = Depends(get_db),
):
    return ApplicationFinancingRepositorySQL(db)


def get_application_option_repository(
    db: Session = Depends(get_db),
):
    return ApplicationOptionRepositorySQL(db)


# =====================================================
# PAYMENTS
# =====================================================

from modules.payments.infrastructure.repositories.payment_repository_sql import (
    PaymentRepositorySQL,
)


def get_payment_repository(
    db: Session = Depends(get_db),
):
    return PaymentRepositorySQL(db)


# =====================================================
# FINANCING 
# =====================================================
from modules.financing.infrastructure.repositories.financing_contract_repository_sql import SqlFinancingContractRepository
from modules.financing.infrastructure.repositories.installment_repository_sql import InstallmentRepositorySQL

def get_financing_contract_repository(
    db: Session = Depends(get_db),
):
    return SqlFinancingContractRepository(db)

def get_installment_repository(
    db: Session = Depends(get_db),
):
    return InstallmentRepositorySQL(db)

# =====================================================
# FAVORITES
# =====================================================

from modules.favorites.infrastructure.repositories.favorite_repository_sql import (
    FavoriteRepositorySQL,
)


def get_favorite_repository(
    db: Session = Depends(get_db),
):
    return FavoriteRepositorySQL(db)

# =====================================================
# INSPECTIONS
# =====================================================

from modules.inspections.infrastructure.repositories.inspection_repository_sql import (
    InspectionRepositorySQL,
)


def get_inspection_repository(
    db: Session = Depends(get_db),
):
    return InspectionRepositorySQL(db)


# =====================================================
# JOB QUEUE
# =====================================================
from modules.vehicles.infrastructure.queue.redis_job_queue import RedisJobQueue


def get_job_queue():
    return RedisJobQueue()


# =====================================================
# LEAD
# =====================================================

from modules.leads.infrastructure.repositories.lead_repository_sql import LeadRepositorySQL
from modules.leads.application.services.LeadAuthorizationService import LeadAuthorizationService

def get_lead_repository(
    db: Session = Depends(get_db),
):
    return LeadRepositorySQL(db)

def get_lead_authorization():

    return LeadAuthorizationService()
# =====================================================
# NOTIFICATIONS
# =====================================================

from modules.notifications.infrastructure.repositories.notification_repository_sql import (
    NotificationRepositorySQL,
)


def get_notification_repository(
    db: Session = Depends(get_db),
):
    return NotificationRepositorySQL(db)


# =====================================================
# OPTIONS
# =====================================================

from modules.options.infrastructure.repositories.option_repository_sql import (
    OptionRepositorySQL,
)


def get_option_repository(
    db: Session = Depends(get_db),
):
    return OptionRepositorySQL(db)

# =====================================================
# RECONDITIONINGS
# =====================================================

from modules.reconditionings.infrastructure.repositories.reconditioning_repository_sql import (
    ReconditioningRepositorySQL,
)


def get_reconditioning_repository(
    db: Session = Depends(get_db),
):
    return ReconditioningRepositorySQL(db)

# =====================================================
# RESERVATIONS
# =====================================================

from modules.reservations.infrastructure.repositories.reservation_repository_sql import (
    ReservationRepositorySQL
)


def get_reservation_repository(
    db: Session = Depends(get_db),
):
    return ReservationRepositorySQL(db)

# =====================================================
# AUTH
# =====================================================

from modules.auth.infrastructure.repositories.user_repository_sql import (
    UserRepositorySQL,
)
from modules.auth.infrastructure.repositories.refresh_token_repository_sql import (
    RefreshTokenRepositorySQL,
)

from modules.auth.infrastructure.repositories.user_activation_token_repository_sql import SQLActivationTokenRepository

def get_user_repository(
    db: Session = Depends(get_db),
):
    return UserRepositorySQL(db)


def get_refresh_repository(
    db: Session = Depends(get_db),
):
    return RefreshTokenRepositorySQL(db)


def get_user_activation_token_repository(
    db: Session = Depends(get_db),
):
    return SQLActivationTokenRepository(db)
# =====================================================
# QUOTE
# =====================================================

from modules.quotes.infrastructure.repositories.quote_repository_sql import QuoteRepositorySQL
from modules.quotes.infrastructure.repositories.quote_trade_in_repository_sql import QuoteTradeInRepositorySQL

def get_quote_repository(
    db: Session = Depends(get_db),
):
    return QuoteRepositorySQL(db)


def get_quote_trade_in_repository(
    db: Session = Depends(get_db),
):
    return QuoteTradeInRepositorySQL(db)

# =====================================================
# TEST DRIVES
# =====================================================

from modules.test_drives.infrastructure.repositories.test_drive_repository_sql import (
    TestDriveRepositorySQL,
)


def get_test_drive_repository(
    db: Session = Depends(get_db),
):
    return TestDriveRepositorySQL(db)


# =====================================================
# VEHICLES
# =====================================================

from modules.vehicles.infrastructure.repositories.vehicle_repository_sql import (
    VehicleRepositorySQL,
)
from modules.vehicles.infrastructure.repositories.vehicle_option_repository_sql import (
    VehicleOptionRepositorySQL,
)

def get_vehicle_repository(
    db: Session = Depends(get_db),
):
    return VehicleRepositorySQL(db)


def get_vehicle_option_repository(
    db: Session = Depends(get_db),
):
    return VehicleOptionRepositorySQL(db)


# =====================================================
# WARRANTIES
# =====================================================

from modules.warranties.infrastructure.repositories.warranty_plan_repository_sql import (
    WarrantyPlanRepositorySQL,
)
from modules.warranties.infrastructure.repositories.vehicle_warranty_repository_sql import (
    VehicleWarrantyRepositorySQL,
)


def get_warranty_plan_repository(
    db: Session = Depends(get_db),
):
    return WarrantyPlanRepositorySQL(db)


def get_vehicle_warranty_repository(
    db: Session = Depends(get_db),
):
    return VehicleWarrantyRepositorySQL(db)


# =====================================================
# SAV
# =====================================================
from modules.sav.infrastructure.repositories.support_ticket_repository_sql import SupportTicketSQLRepository


def get_ticket_repository(db: Session = Depends(get_db)):
    return SupportTicketSQLRepository(db)

from modules.sav.infrastructure.repositories.ticket_message_repository_sql import TicketMessageSQLRepository

def get_ticket_message_repository(db: Session = Depends(get_db)):
    return TicketMessageSQLRepository(db)

from modules.sav.infrastructure.repositories.ticket_read_state_repository_sql import TicketReadStateRepositorySQL

def get_ticket_read_state_repository(db: Session = Depends(get_db)):
    return TicketReadStateRepositorySQL(db)

from modules.sav.application.ticket_chat_manager import ticket_chat_manager

def get_ticket_chat_manager():
    return ticket_chat_manager

# =====================================================
# WEBSOCKET
# =====================================================
from modules.notifications.application.services.websocket_manager import manager

def get_websocket_manager():
    return manager

