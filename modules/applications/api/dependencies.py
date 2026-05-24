from fastapi import Depends
import os
from infrastructure.db.dependencies import get_db

from fastapi import Depends
from sqlalchemy.orm import Session


from modules.applications.infrastructure.repositories.application_repository_sql import (
    ApplicationRepositorySQL
)
from modules.applications.infrastructure.repositories.document_repository_sql import (
    DocumentRepositorySQL
)
from modules.applications.infrastructure.repositories.event_repository_sql import (
    EventRepositorySQL
)
from modules.applications.domain.repositories.application_repository import (
    ApplicationRepository
)

from modules.applications.application.use_cases.save_draft_application_use_case import (
    SaveDraftApplicationUseCase
)
from modules.applications.application.use_cases.admin.update_document import (
    UpdateDocumentUseCase
)


from modules.financing.domain.services.trade_in_service import (
    TradeInService
)

from modules.financing.domain.services.financing_service import (
    FinancingService
)
from modules.applications.application.use_cases.get_application_by_vehicle import GetApplicationByVehicleUseCase
from modules.applications.application.use_cases.get_application import GetApplicationUseCase


def get_application_repository(
    db: Session = Depends(get_db),
) -> ApplicationRepository:

    return ApplicationRepositorySQL(db)



def get_event_repository(
    db: Session = Depends(get_db)
):

    return EventRepositorySQL(db)


def get_trade_in_service():
    return TradeInService()


def get_financing_service():
    return FinancingService()

def get_save_draft_use_case(
    repo: ApplicationRepository = Depends(get_application_repository),
    trade_in_service: TradeInService = Depends(get_trade_in_service),
    financing_service: FinancingService = Depends(get_financing_service),
    event_repository: EventRepository = Depends(get_event_repository)
):

    return SaveDraftApplicationUseCase(
        application_repository=repo,
        trade_in_service=trade_in_service,
        financing_service=financing_service,
        event_repository=event_repository
    )





def get_application_by_vehicle_usecase(
    application_repository: ApplicationRepository = Depends(
        get_application_repository
    )
):

    return GetApplicationByVehicleUseCase(
        application_repository=application_repository
    )





from modules.applications.application.use_cases.get_application import (
    GetApplicationUseCase
)


def get_application_usecase(
    application_repository: ApplicationRepository = Depends(
        get_application_repository
    )
):

    return GetApplicationUseCase(
        application_repository=application_repository
    )





# =========================================
# app/presentation/dependencies/application_dependencies.py
# =========================================


from modules.applications.application.use_cases.get_applications import (
    GetApplicationsUseCase
)




def get_applications_usecase(

    repository: ApplicationRepositorySQL = Depends(
        get_application_repository
    )

):

    return GetApplicationsUseCase(
        application_repository=repository
    )







def get_document_repository(
    db: Session = Depends(get_db)
):

    return DocumentRepositorySQL(db)


def get_update_document_usecase(
    repo=Depends(get_document_repository),
    event_repo=Depends(get_event_repository)
):

    return UpdateDocumentUseCase(
        document_repository=repo,
        event_repository=event_repo
    )








from fastapi import Depends











from modules.applications.application.use_cases.admin.update_application_status import UpdateApplicationStatusUseCase
from modules.notifications.api.dependencies import (
    get_notification_service,
    get_notification_repository)



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

from modules.applications.infrastructure.repositories.application_trade_in_repository_sql import ApplicationTradeInRepositorySQL
from modules.applications.infrastructure.repositories.application_financing_repository_sql import ApplicationFinancingRepositorySQL
from modules.applications.infrastructure.repositories.application_option_repository_sql import ApplicationOptionRepositorySQL

def get_trade_in_repository(
    db: Session = Depends(get_db)
):

    return ApplicationTradeInRepositorySQL(db)



def get_financing_repository(
    db: Session = Depends(get_db)
):

    return ApplicationFinancingRepositorySQL(db)


def get_application_option_repository(
    db: Session = Depends(get_db)
):

    return ApplicationOptionRepositorySQL(db)


from modules.applications.application.use_cases.delete_application import DeleteApplicationUseCase
from modules.storage.api.dependencies import get_s3_service

def get_delete_application_usecase(
    application_repository=Depends(get_application_repository),
    document_repository=Depends(get_document_repository),
    trade_in_repository=Depends(get_trade_in_repository),
    financing_repository=Depends(get_financing_repository),
    application_option_repository=Depends(get_application_option_repository),
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
        event_repo=event_repository,
        notification_repo=notification_repository,
        s3_service=s3_service
    )





from modules.applications.application.use_cases.get_applications import (
    GetApplicationsUseCase
)

def get_applications_usecase(

    application_repository=Depends(
        get_application_repository
    )
):

    return GetApplicationsUseCase(
        application_repository=application_repository
    )







from modules.applications.infrastructure.repositories.application_repository_sql import (
    ApplicationRepositorySQL
)

from modules.applications.application.use_cases.admin.archive_application import (
    ArchiveApplicationUseCase
)

from modules.applications.application.use_cases.admin.unarchive_application import (
    UnarchiveApplicationUseCase
)

from modules.applications.application.use_cases.admin.soft_delete_application import (
    SoftDeleteApplicationUseCase
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




from modules.applications.application.use_cases.submit_application import SubmitApplicationUseCase


def get_submit_application_usecase(
    repo: ApplicationRepositorySQL = Depends(get_application_repository)
):
    return SubmitApplicationUseCase(application_repository=repo)







def get_submit_usecase(
    application_repo=Depends(get_application_repository),
    event_repo=Depends(get_event_repository),
    financing_service=Depends(get_financing_service),
    trade_in_service=Depends(get_trade_in_service),
):
    return SubmitApplicationUseCase(
        application_repository=application_repo,
        event_repository=event_repo,
        financing_service=financing_service,
        trade_in_service=trade_in_service
    )





# Use cases
from modules.applications.application.use_cases.update_application import UpdateApplicationFull

# Repositories (interfaces ou implémentations)
from modules.applications.domain.repositories.application_repository import ApplicationRepository
from modules.vehicles.domain.repositories.vehicle_repository import VehicleRepository
from modules.applications.domain.repositories.event_repository import EventRepository
from modules.applications.domain.repositories.application_option_repository import ApplicationOptionRepository
from modules.vehicles.domain.repositories.vehicle_option_repository import VehicleOptionRepository


# Dependency providers (infra)
from modules.vehicles.api.dependencies import (get_vehicle_repository, get_vehicle_option_repository)

# REPOSITORIES
# =====================







# =====================
# SERVICES
# =====================





























