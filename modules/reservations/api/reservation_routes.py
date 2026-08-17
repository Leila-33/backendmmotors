from fastapi import APIRouter, Depends

from modules.reservations.api.schemas import (
    CheckAvailabilityRequest,
    CheckAvailabilityResponse,
)

from modules.reservations.application.dtos.check_availability_dto import (
    CheckAvailabilityDTO,
)

from modules.reservations.application.use_cases.check_availability import (
    CheckReservationAvailabilityUseCase,
)

from modules.reservations.api.dependencies import (
    get_check_availability_usecase,
)


router = APIRouter(
    tags=["Reservations"]
)


# =========================================================
# CHECK AVAILABILITY
# =========================================================

@router.get(
    "/check",
    response_model=CheckAvailabilityResponse,
)
def check_reservation_availability(

    request: CheckAvailabilityRequest,

    usecase: CheckReservationAvailabilityUseCase = Depends(
        get_check_availability_usecase
    ),

):

    # =====================================================
    # DTO
    # =====================================================

    dto = CheckAvailabilityDTO(
        vehicle_id=request.vehicle_id,
        start_date=request.start_date,
        end_date=request.end_date,
    )

    # =====================================================
    # USE CASE
    # =====================================================

    result = usecase.execute(
        dto
    )

    # =====================================================
    # RESPONSE
    # =====================================================

    return CheckAvailabilityResponse(
        available=result.available
    )