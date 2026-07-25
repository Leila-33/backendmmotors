from fastapi import Depends

from modules.reservations.api.dependencies import get_cancel_uc
# =========================
# USE CASES
# =========================
from modules.applications.application.use_cases.save_draft_application_use_case import SaveDraftApplicationUseCase
from modules.applications.application.use_cases.get_application import GetApplicationUseCase
from modules.applications.application.use_cases.get_applications import GetApplicationsUseCase
from modules.applications.application.use_cases.get_application_by_vehicle import GetApplicationByVehicleUseCase
from modules.applications.application.use_cases.submit_application import SubmitApplicationUseCase
from modules.applications.application.use_cases.delete_application import DeleteApplicationUseCase

# ADMIN USE CASES
from modules.applications.application.use_cases.admin.update_document import UpdateDocumentUseCase
from modules.applications.application.use_cases.admin.update_application_status import UpdateApplicationStatusUseCase
from modules.applications.application.use_cases.admin.archive_application import ArchiveApplicationUseCase
from modules.applications.application.use_cases.admin.unarchive_application import UnarchiveApplicationUseCase
from modules.applications.application.use_cases.admin.soft_delete_application import SoftDeleteApplicationUseCase
from modules.applications.application.use_cases.cancel_application import CancelApplicationUseCase

# =========================
# REPOSITORIES / SERVICES TYPES
# =========================
from modules.applications.domain.repositories.application_repository import ApplicationRepository
from modules.applications.domain.repositories.event_repository import EventRepository
from modules.financing.domain.services.financing_service import FinancingService
from modules.financing.domain.services.trade_in_service import TradeInService
from modules.reservations.domain.repositories.reservation_repository import ReservationRepository

# =========================
# CORE DEPENDENCIES
# =========================
from modules.dependencies.dependencies import (
    get_application_repository,
    get_event_repository,
    get_document_repository,
    get_trade_in_repository,
    get_financing_repository,
    get_application_option_repository,
    get_payment_repository,
    get_trade_in_service,
    get_financing_service,
    get_reservation_repository
)

# =========================
# EXTERNAL SERVICES
# =========================
from modules.notifications.api.dependencies import get_notification_service
from modules.dependencies.dependencies import (
    get_s3_service,
    get_notification_repository
)



def get_save_draft_use_case(
    repo: ApplicationRepository = Depends(get_application_repository),
    reservation_repo: ReservationRepository = Depends(get_reservation_repository),
    trade_in_service: TradeInService = Depends(get_trade_in_service),
    financing_service: FinancingService = Depends(get_financing_service),
    event_repository: EventRepository = Depends(get_event_repository)
):

    return SaveDraftApplicationUseCase(
        application_repository=repo,
        reservation_repository=reservation_repo,
        trade_in_service=trade_in_service,
        financing_service=financing_service,
        event_repository=event_repository
    )



def get_application_usecase(
    application_repository: ApplicationRepository = Depends(
        get_application_repository
    ),
    payment_repository =  Depends(get_payment_repository)
):

    return GetApplicationUseCase(
        application_repository=application_repository,
        payment_repository=payment_repository
    )


def get_application_by_vehicle_usecase(
    application_repository: ApplicationRepository = Depends(
        get_application_repository
    )
):

    return GetApplicationByVehicleUseCase(
        application_repository=application_repository
    )


def get_applications_usecase(
    application_repository=Depends(get_application_repository),
    reservation_repository=Depends(get_reservation_repository)
):

    return GetApplicationsUseCase(
        application_repository=application_repository,
        reservation_repository=reservation_repository
    )


def get_update_document_usecase(
    repo=Depends(get_document_repository),
    event_repo=Depends(get_event_repository),
    notification_service=Depends(get_notification_service)
):

    return UpdateDocumentUseCase(
        document_repository=repo,
        event_repository=event_repo,
        notification_service=notification_service
    )


def get_update_application_status_usecase(

    application_repository = Depends(
        get_application_repository
    ),

    notification_service = Depends(
        get_notification_service
    ),
    event_repository: EventRepository = Depends(get_event_repository)


):

    return UpdateApplicationStatusUseCase(
        application_repository=application_repository,
        notification_service=notification_service,
        event_repository=event_repository
    )




def get_delete_application_usecase(
    application_repository=Depends(get_application_repository),
    document_repository=Depends(get_document_repository),
    trade_in_repository=Depends(get_trade_in_repository),
    financing_repository=Depends(get_financing_repository),
    application_option_repository=Depends(get_application_option_repository),
    reservation_repo=Depends(get_reservation_repository),
    event_repository=Depends(get_event_repository),
    notification_repository=Depends(get_notification_repository),
    s3_service=Depends(get_s3_service)
):

    return DeleteApplicationUseCase(
        application_repo=application_repository,
        document_repo=document_repository,
        trade_in_repo=trade_in_repository,
        financing_repo=financing_repository,
        application_option_repo=application_option_repository,
        reservation_repo=reservation_repo,
        event_repo=event_repository,
        notification_repo=notification_repository,
        s3_service=s3_service
    )




def get_archive_usecase(
    repo = Depends(get_application_repository),
    event_repository: EventRepository = Depends(get_event_repository)
):

    return ArchiveApplicationUseCase(repo, event_repository)


def get_unarchive_usecase(
    repo = Depends(get_application_repository),
    event_repository: EventRepository = Depends(get_event_repository)
):

    return UnarchiveApplicationUseCase(repo, event_repository)



def get_soft_delete_usecase(
    repo = Depends(get_application_repository)
):

    return SoftDeleteApplicationUseCase(repo)

def get_submit_usecase(
    application_repo=Depends(get_application_repository),
    event_repo=Depends(get_event_repository),
    financing_service=Depends(get_financing_service),
    trade_in_service=Depends(get_trade_in_service),
    reservation_repo=Depends(get_reservation_repository)
):
    return SubmitApplicationUseCase(
        application_repository=application_repo,
        event_repository=event_repo,
        financing_service=financing_service,
        trade_in_service=trade_in_service,
        reservation_repository=reservation_repo
    )

def get_cancel_application_usecase(
    application_repo = Depends(get_application_repository),
    reservation_repo = Depends(get_reservation_repository),
    financing_repo = Depends(get_financing_repository),
    event_repo = Depends(get_event_repository),
    cancel_reservation_uc=Depends(get_cancel_uc)
) -> CancelApplicationUseCase:

    return CancelApplicationUseCase(
        application_repository=application_repo,
        reservation_repository=reservation_repo,
        financing_contract_repository=financing_repo,
        event_repository=event_repo,
        cancel_reservation_uc=cancel_reservation_uc
    )

from modules.applications.application.use_cases.admin.restore_cancelled_application import RestoreCancelledApplicationUseCase
def get_restore_cancelled_usecase(
    application_repository=Depends(get_application_repository),
    reservation_repository=Depends(get_reservation_repository),
    event_repository=Depends(get_event_repository),
):

    return RestoreCancelledApplicationUseCase(
        application_repository=application_repository,
        reservation_repository=reservation_repository,
        event_repository=event_repository
    )














