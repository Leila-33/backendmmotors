from fastapi import Depends
from modules.reservations.application.use_cases.create_reservation import CreateReservationUseCase
from modules.reservations.application.use_cases.cancel_reservation import CancelReservationUseCase
from modules.reservations.application.use_cases.complete_expired_rentals import CompleteExpiredRentalsUseCase
from modules.dependencies.dependencies import (
    get_reservation_repository,
    get_event_repository,
    get_application_repository
)


def get_create_uc(repo=Depends(get_reservation_repository)):
    return CreateReservationUseCase(repo)


def get_cancel_uc(
    reservation_repo=Depends(get_reservation_repository),
    event_repo=Depends(get_event_repository)
):

    return CancelReservationUseCase(
        reservation_repository=reservation_repo,
        event_repository=event_repo
    )

def get_complete_rentals_usecase(
    reservation_repo=Depends(get_reservation_repository),
    event_repo=Depends(get_event_repository),
    application_repo=Depends(get_application_repository)

):
    return CompleteExpiredRentalsUseCase(
        reservation_repository=reservation_repo,
        event_repository=event_repo,
        application_repository=application_repo

    )

