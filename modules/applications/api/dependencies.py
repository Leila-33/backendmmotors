from fastapi import Depends

from modules.reservations.api.dependencies import get_cancel_reservation_usecase
# =========================
# USE CASES
# =========================
from modules.applications.application.use_cases.save_draft_application import SaveDraftApplicationUseCase
from modules.applications.application.use_cases.get_application import GetApplicationUseCase
from modules.applications.application.use_cases.get_applications import GetApplicationsUseCase
from modules.applications.application.use_cases.get_application_by_vehicle import GetApplicationByVehicleUseCase
from modules.applications.application.use_cases.submit_application import SubmitApplicationUseCase
from modules.applications.application.use_cases.delete_application import DeleteApplicationUseCase

# =========================
# ADMIN USE CASES
# =========================
from modules.applications.application.use_cases.admin.update_document import UpdateDocumentUseCase
from modules.applications.application.use_cases.admin.update_application_status import UpdateApplicationStatusUseCase
from modules.applications.application.use_cases.admin.archive_application import ArchiveApplicationUseCase
from modules.applications.application.use_cases.admin.unarchive_application import UnarchiveApplicationUseCase
from modules.applications.application.use_cases.admin.soft_delete_application import SoftDeleteApplicationUseCase
from modules.applications.application.use_cases.cancel_application import CancelApplicationUseCase
from modules.reservations.application.use_cases.cancel_reservation import CancelReservationUseCase
from modules.applications.application.use_cases.admin.soft_delete_application import SoftDeleteApplicationUseCase
from modules.applications.application.use_cases.admin.restore_cancelled_application import RestoreCancelledApplicationUseCase
from modules.applications.application.use_cases.admin.get_events import GetEventsUseCase

# =========================
# REPOSITORIES / SERVICES TYPES
# =========================
from modules.applications.domain.repositories.application_repository import ApplicationRepository
from modules.payments.domain.repositories.payment_repository import PaymentRepository
from modules.reservations.domain.repositories.reservation_repository import ReservationRepository
from modules.applications.application.services.document_sync_service import DocumentSyncService
from modules.financing.domain.repositories.financing_contract_repository import FinancingContractRepository
from modules.applications.domain.repositories.document_repository import DocumentRepository

# =========================
# DEPENDENCIES
# =========================
from modules.dependencies.dependencies import (
    get_application_repository,
    get_payment_repository,
    get_vehicle_repository,
    get_event_repository,
    get_document_repository,
    get_trade_in_repository,
    get_financing_repository,
    get_application_option_repository,
    get_option_repository,
    get_reservation_repository,
    get_notification_repository,
    get_trade_in_repository,
    get_financing_repository,
    get_event_service
)
from modules.financing.api.dependencies import (
    get_trade_in_service,
    get_financing_service
)
# =========================
# EXTERNAL SERVICES
# =========================
from modules.storage.api.dependencies import (
    get_s3_service
)
from modules.notifications.api.dependencies import get_notification_service
from modules.storage.infrastructure.s3_service import S3Service
from modules.applications.application.services.restore_application_service import RestoreApplicationService


# =========================
# CORE
# =========================
from core.database.dependencies import (
    get_unit_of_work
)
from core.database.unit_of_work import UnitOfWork

# =========================
# FACTORIES
# =========================
from modules.applications.api.application_response_factory import ApplicationResponseFactory
from modules.applications.api.application_list_response_factory import ApplicationListResponseFactory


# =====================================================
# SERVICES
# =====================================================
from modules.applications.application.services.application_form_service import ApplicationFormService
from modules.applications.application.services.document_sync_service import DocumentSyncService
from modules.applications.application.services.rental_duration_calculator import RentalDurationCalculator
from modules.applications.application.services.pricing_calculator import PricingCalculator


def get_document_sync_service(
    document_repository: DocumentRepository = Depends(
        get_document_repository
    ),
    s3_service: S3Service = Depends(
        get_s3_service
    ),
) -> DocumentSyncService:

    return DocumentSyncService(
        document_repository=document_repository,
        s3_service=s3_service,
    )


def get_application_form_service(
    application_repository=Depends(
        get_application_repository
    ),

    vehicle_repository=Depends(
        get_vehicle_repository
    ),

    trade_in_repository=Depends(
        get_trade_in_repository
    ),

    trade_in_service=Depends(
        get_trade_in_service
    ),

    financing_repository=Depends(
        get_financing_repository
    ),

    financing_service=Depends(
        get_financing_service
    ),

    application_option_repository=Depends(
        get_application_option_repository
    ),

    option_repository=Depends(
        get_option_repository
    ),

    document_sync_service=Depends(
        get_document_sync_service
    ),

    reservation_repository=Depends(
        get_reservation_repository
    ),

    rental_duration_calculator=Depends(
        RentalDurationCalculator
    ),

    pricing_calculator=Depends(
        PricingCalculator
    ),
):

    return ApplicationFormService(
        application_repository=(
            application_repository
        ),

        vehicle_repository=(
            vehicle_repository
        ),

        trade_in_repository=(
            trade_in_repository
        ),

        trade_in_service=(
            trade_in_service
        ),

        financing_repository=(
            financing_repository
        ),

        financing_service=(
            financing_service
        ),

        application_option_repository=(
            application_option_repository
        ),

        option_repository=(
            option_repository
        ),

        document_sync_service=(
            document_sync_service
        ),

        reservation_repository=(
            reservation_repository
        ),

        rental_duration_calculator=(
            rental_duration_calculator
        ),

        pricing_calculator=(
            pricing_calculator
        ),
    )


# =========================
# CLIENT
# =========================
def get_save_draft_application_usecase(
    application_form_service=Depends(
        get_application_form_service
    ),
    event_service=Depends(get_event_service),
    uow=Depends(
        get_unit_of_work
    ),
):

    return SaveDraftApplicationUseCase(
        application_form_service=(
            application_form_service
        ),
        event_service=event_service,
        uow=uow,
    )

def get_submit_application_usecase(
    application_form_service=Depends(
        get_application_form_service
    ),
    application_repository=Depends(
        get_application_repository
    ),
    reservation_repository=Depends(
        get_reservation_repository
    ),
    event_service=Depends(get_event_service),
    uow: UnitOfWork = Depends(
        get_unit_of_work
    ),
):

    return SubmitApplicationUseCase(
        application_form_service=application_form_service,
        application_repository=application_repository,
        reservation_repository=reservation_repository,
        event_service=event_service,
        uow=uow,
    )

def get_application_response_factory(
    s3_service: S3Service = Depends(get_s3_service)
):
    return ApplicationResponseFactory(
        s3_service=s3_service
    )


def get_application_usecase(
    application_repository: ApplicationRepository = Depends(
        get_application_repository
    ),
    payment_repository: PaymentRepository = Depends(
        get_payment_repository
    )
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





def get_application_list_response_factory(
) -> ApplicationListResponseFactory:

    return ApplicationListResponseFactory()

def get_restore_application_service(
    reservation_repository: ReservationRepository = Depends(
        get_reservation_repository
    )
) -> RestoreApplicationService:

    return RestoreApplicationService(
        reservation_repository=reservation_repository
    )

def get_get_applications_usecase(
    application_repository: ApplicationRepository = Depends(
        get_application_repository
    ),
    restore_application_service: RestoreApplicationService = Depends(
        get_restore_application_service
    ),
) -> GetApplicationsUseCase:

    return GetApplicationsUseCase(
        application_repository=application_repository,
        restore_application_service=restore_application_service,
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
    s3_service=Depends(get_s3_service),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work
    ),
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
        s3_service=s3_service,
        uow=unit_of_work    
    )


def get_cancel_application_usecase(
    application_repo: ApplicationRepository = Depends(
        get_application_repository
    ),
    financing_contract_repo: FinancingContractRepository = Depends(
        get_financing_repository
    ),
    event_service=Depends(get_event_service),
    cancel_reservation_uc: CancelReservationUseCase = Depends(
        get_cancel_reservation_usecase
    ),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work
    ),
) -> CancelApplicationUseCase:

    return CancelApplicationUseCase(
        application_repository=application_repo,
        financing_contract_repository=financing_contract_repo,
        event_service=event_service,
        cancel_reservation_uc=cancel_reservation_uc,
        unit_of_work=unit_of_work,
    )

# =========================
# ADMIN
# =========================
def get_restore_cancelled_usecase(
    application_repository: ApplicationRepository = Depends(
        get_application_repository
    ),
    reservation_repository: ReservationRepository = Depends(
        get_reservation_repository
    ),
    event_service=Depends(get_event_service),
    restore_application_service: RestoreApplicationService = Depends(
        get_restore_application_service
    ),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work
    ),
) -> RestoreCancelledApplicationUseCase:

    return RestoreCancelledApplicationUseCase(
        application_repository=application_repository,
        reservation_repository=reservation_repository,
        event_service=event_service,
        restore_application_service=restore_application_service,
        unit_of_work=unit_of_work,
    )

def get_archive_application_usecase(
    application_repository: ApplicationRepository = Depends(
        get_application_repository
    ),
    event_service=Depends(get_event_service),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work
    ),
) -> ArchiveApplicationUseCase:

    return ArchiveApplicationUseCase(
        application_repository=application_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )

def get_unarchive_application_usecase(
    application_repository: ApplicationRepository = Depends(
        get_application_repository
    ),
    event_service=Depends(get_event_service),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work
    ),
) -> UnarchiveApplicationUseCase:

    return UnarchiveApplicationUseCase(
        application_repository=application_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )



def get_soft_delete_application_usecase(
    application_repository: ApplicationRepository = Depends(
        get_application_repository
    ),
    event_service=Depends(get_event_service),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work
    ),
) -> SoftDeleteApplicationUseCase:

    return SoftDeleteApplicationUseCase(
        application_repository=application_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


def get_update_document_usecase(
    repo=Depends(get_document_repository),
    application_repo=Depends(get_application_repository),
    event_service=Depends(get_event_service),
    notification_service=Depends(get_notification_service),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work
    ),
):

    return UpdateDocumentUseCase(
        document_repository=repo,
        application_repository=application_repo,
        event_service=event_service,
        notification_service=notification_service,
        uow=unit_of_work,
    )


def get_update_application_status_usecase(

    application_repository = Depends(
        get_application_repository
    ),

    notification_service = Depends(
        get_notification_service
    ),
    event_service=Depends(get_event_service),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work
    ),


):

    return UpdateApplicationStatusUseCase(
        application_repository=application_repository,
        notification_service=notification_service,
        event_service=event_service,
        uow=unit_of_work,
    )


def get_events_usecase(
    event_repository=Depends(
        get_event_repository
    )
):

    return GetEventsUseCase(
        event_repository
    )






