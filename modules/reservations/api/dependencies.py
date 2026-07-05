from fastapi import Depends
from modules.reservations.application.use_cases.create_reservation import CreateReservationUseCase
from modules.reservations.application.use_cases.cancel_reservation import CancelReservationUseCase
from modules.core.infrastructure.dependencies import get_reservation_repository, get_event_repository
    

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