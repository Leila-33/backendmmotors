from modules.reservations.application.dtos.check_availability_dto import (
    CheckAvailabilityDTO,
)
from modules.reservations.domain.repositories.reservation_repository import ReservationRepository

class CheckReservationAvailabilityUseCase:
    """
    Vérifie la disponibilité d'un véhicule pour une période donnée
    en recherchant l'existence d'une réservation qui se chevauche.
    """
    def __init__(
        self,
        reservation_repository: ReservationRepository,
    ):
        self.reservation_repository = reservation_repository


    def execute(
        self,
        dto: CheckAvailabilityDTO
    ) -> bool:

        overlapping = (
            self.reservation_repository.exists_overlap(
                vehicle_id=dto.vehicle_id,
                start_date=dto.start_date,
                end_date=dto.end_date,
            )
        )

        return not overlapping