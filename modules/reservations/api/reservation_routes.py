from fastapi import APIRouter, Depends

from modules.reservations.api.schemas import (
    ReservationCreate,
    ReservationCheck
)

from modules.reservations.application.use_cases.reservation import (
    CreateReservationUseCase,
    CancelReservationUseCase
)
from modules.reservations.api.dependencies import (
    get_create_uc,
    get_cancel_uc,
    get_repo
)
from core.security.dependencies import get_current_user

from modules.reservations.infrastructure.repositories.reservation_repository_sql import ReservationRepositorySQL


router = APIRouter(tags=["Reservations"])



# =========================
# CREATE
# =========================
@router.post("/")
def create_reservation(
    data: ReservationCreate,
    uc: CreateReservationUseCase = Depends(get_create_uc),
    user=Depends(get_current_user)   # ✅ ICI
):
    return uc.execute(data, user.id)


# =========================
# CANCEL
# =========================
@router.delete("/{reservation_id}")
def cancel_reservation(
    reservation_id: int,
    uc: CancelReservationUseCase = Depends(get_cancel_uc),
    user=Depends(get_current_user)   # ✅ ICI
):
    return uc.execute(reservation_id, user.id)


# =========================
# CHECK AVAILABILITY
# =========================
@router.post("/check")
def check_availability(
    data: ReservationCheck,
    repo: ReservationRepositorySQL = Depends(get_repo),
):
    overlapping = repo.exists_overlap(
        data.vehicle_id,
        data.start_date,
        data.end_date
    )

    return {
        "available": not overlapping
    }