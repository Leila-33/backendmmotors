from modules.applications.domain.exceptions import CannotRestoreApplication
from modules.vehicles.domain.enums import VehicleType
from datetime import date

class RestoreApplicationService:

    def __init__(
        self,
        reservation_repository
    ):
        self.reservation_repository = reservation_repository


    def validate_rental(
        self,
        application
    ):

        if application.vehicle.type != VehicleType.RENT:
            return


        reservation = application.reservation


        if not reservation:
            raise CannotRestoreApplication(
                "Réservation introuvable."
            )


        if date.today() >= reservation.start_date:
            raise CannotRestoreApplication(
                "La période de location a commencé."
            )


        if self.reservation_repository.exists_overlap(
            vehicle_id=reservation.vehicle_id,
            start_date=reservation.start_date,
            end_date=reservation.end_date,
        ):
            raise CannotRestoreApplication(
                "Le véhicule n'est plus disponible."
            )