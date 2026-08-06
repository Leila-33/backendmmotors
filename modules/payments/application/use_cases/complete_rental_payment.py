from modules.applications.domain.enums import ApplicationStatus, EventType
from modules.vehicles.domain.enums import VehicleStatus
from modules.applications.domain.enums import (
    EventType,
)
from modules.vehicles.domain.enums import VehicleStatus
from modules.applications.domain.enums import (
    EventType
)
from modules.payments.api.schemas import (
    CompleteRentalPaymentResponse
)

class CompleteRentalPaymentUseCase:


    def __init__(
        self,
        vehicle_repository,
        application_repository,
        event_service,
    ):

        self.vehicle_repository = vehicle_repository
        self.application_repository = application_repository
        self.event_service = event_service



    def execute(
        self,
        application,
        payment,
    ):


        vehicle = application.vehicle



        # =========================
        # RENTAL START
        # =========================

        vehicle.status = (
            VehicleStatus.IN_RENTAL
        )

        vehicle.is_available = False


        self.vehicle_repository.update(
            vehicle
        )



        # =========================
        # APPLICATION
        # =========================

        application.status = (
            ApplicationStatus.COMPLETED
        )


        self.application_repository.update(
            application
        )



        self.event_service.log(
            type=EventType.RENTAL_PAYMENT_PAID,
            application_id=application.id,
            user_id=application.user_id,
            message="Paiement location confirmé",
            event_metadata={
                "payment_id": payment.id,
                "vehicle_id": vehicle.id,
            }
        )

        return CompleteRentalPaymentResponse(

    application_id=application.id,

    vehicle_id=vehicle.id,

    rental_started=True,

    message=(
        "Location activée avec succès"
    )
)