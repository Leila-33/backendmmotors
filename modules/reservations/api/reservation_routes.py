from fastapi import APIRouter, Depends

from modules.reservations.api.schemas import (
    ReservationCheck,
    ReservationResponseDTO,
    CreateReservationDTO,
    CancelReservationDTO
)
from modules.reservations.application.use_cases.create_reservation import CreateReservationUseCase
from modules.reservations.application.use_cases.cancel_reservation import CancelReservationUseCase
from modules.dependencies.dependencies import (
    get_reservation_repository
    )
from modules.reservations.api.dependencies import (
    get_create_uc,
    get_cancel_uc
)

from core.security.dependencies import get_current_user

from modules.reservations.infrastructure.repositories.reservation_repository_sql import ReservationRepositorySQL


router = APIRouter(tags=["Reservations"])



# =========================
# CREATE
# =========================
@router.post("", response_model=ReservationResponseDTO)
def create_reservation(
    dto: CreateReservationDTO,
    current_user=Depends(get_current_user),
    usecase: CreateReservationUseCase = Depends(get_create_uc)
):

    reservation = usecase.execute(
        data=dto,
        application_id=dto.application_id
    )

    return ReservationResponseDTO(
        id=reservation.id,
        status=reservation.status,
        message="Réservation créée avec succès"
    )


# =========================
# CANCEL
# =========================
@router.post("/cancel", response_model=ReservationResponseDTO)
def cancel_reservation(
    dto: CancelReservationDTO,
    current_user=Depends(get_current_user),
    usecase: CancelReservationUseCase = Depends(get_cancel_uc)
):

    reservation = usecase.execute(
        reservation_id=dto.reservation_id,
        user_id=current_user.id
    )

    return ReservationResponseDTO(
        id=reservation.id,
        status=reservation.status,
        message="Réservation annulée avec succès"
    )


# =========================
# CHECK AVAILABILITY
# =========================
@router.post("/check")
def check_availability(
    data: ReservationCheck,
    repo: ReservationRepositorySQL = Depends(get_reservation_repository),
):
    overlapping = repo.exists_overlap(
        data.vehicle_id,
        data.start_date,
        data.end_date
    )

    return {
        "available": not overlapping
    }