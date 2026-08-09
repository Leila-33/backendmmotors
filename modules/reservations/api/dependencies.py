from fastapi import Depends
from modules.reservations.application.use_cases.create_reservation import CreateReservationUseCase
from modules.reservations.application.use_cases.cancel_reservation import CancelReservationUseCase
from modules.reservations.application.use_cases.check_availability import CheckReservationAvailabilityUseCase
from modules.reservations.application.use_cases.complete_expired_rentals import CompleteExpiredRentalsUseCase
from modules.dependencies.dependencies import (
    get_reservation_repository,
    get_application_repository,
    get_event_service
)

from modules.applications.domain.repositories.application_repository import ApplicationRepository
from modules.reservations.domain.repositories.reservation_repository import ReservationRepository

# =========================
# CORE
# =========================
from core.database.dependencies import (
    get_unit_of_work
)
from core.database.unit_of_work import UnitOfWork


def get_create_reservation_usecase(
    application_repository: ApplicationRepository = Depends(
        get_application_repository
    ),
    reservation_repository: ReservationRepository = Depends(
        get_reservation_repository
    ),
    event_service=Depends(get_event_service),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work
    ),
) -> CreateReservationUseCase:

    return CreateReservationUseCase(
        application_repository=application_repository,
        reservation_repository=reservation_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


def get_cancel_reservation_usecase(
    reservation_repo=Depends(get_reservation_repository),
    event_service=Depends(get_event_service),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work
    )
):

    return CancelReservationUseCase(
        reservation_repository=reservation_repo,
        event_service=event_service,
        unit_of_work=unit_of_work
    )



def get_check_availability_usecase(
    reservation_repository: ReservationRepository = Depends(
        get_reservation_repository
    )
) -> CheckReservationAvailabilityUseCase:

    return CheckReservationAvailabilityUseCase(
        reservation_repository=reservation_repository
    )


def get_complete_rentals_usecase(
    reservation_repo=Depends(get_reservation_repository),
    event_service=Depends(get_event_service),
    application_repo=Depends(get_application_repository),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work
    )
):
    return CompleteExpiredRentalsUseCase(
        reservation_repository=reservation_repo,
        event_service=event_service,
        application_repository=application_repo,
        unit_of_work=unit_of_work
    )

