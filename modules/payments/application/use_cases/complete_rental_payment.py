import logging

from modules.applications.domain.enums import (
    ApplicationStatus,
    EventType,
)
from modules.vehicles.domain.enums import VehicleStatus
from modules.applications.domain.exceptions import (
    ApplicationNotFound,
)

from modules.payments.application.dtos.complete_rental_payment_dto import (
    CompleteRentalPaymentDTO,
)

from modules.payments.application.results.complete_rental_payment_result import (
    CompleteRentalPaymentResult,
)


logger = logging.getLogger(__name__)


class CompleteRentalPaymentUseCase:
    """
    Finalise le paiement d'une location en passant le dossier
    à l'état terminé et en enregistrant l'événement de paiement.

    Le traitement est idempotent afin d'éviter de finaliser
    plusieurs fois une même location.
    """
    def __init__(
        self,
        application_repository,
        event_service,
    ):
        self.application_repository = application_repository
        self.event_service = event_service

    def execute(
        self,
        dto: CompleteRentalPaymentDTO,
    ):

        try:

            # =========================
            # GET APPLICATION
            # =========================

            application = (
                self.application_repository
                .get_by_id(dto.application_id)
            )

            if application is None:
                raise ApplicationNotFound()

            vehicle = application.vehicle

            # =========================
            # IDEMPOTENCE
            # =========================

            if application.status == ApplicationStatus.COMPLETED:

                logger.info(
                    "Location déjà activée",
                    extra={
                        "application_id": application.id,
                        "vehicle_id": vehicle.id,
                        "payment_id": dto.payment_id,
                    },
                )

                return CompleteRentalPaymentResult(
                    application_id=application.id,
                    vehicle_id=vehicle.id,
                    rental_started=True,
                    message="Location déjà activée",
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

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                type=EventType.RENTAL_PAYMENT_PAID,
                application_id=application.id,
                vehicle_id=vehicle.id,
                user_id=application.user_id,
                message="Paiement location confirmé",
                event_metadata={
                    "payment_id": dto.payment_id,
                    "vehicle_id": vehicle.id,
                },
            )

            # =========================
            # LOG SUCCESS
            # =========================

            logger.info(
                "Location activée après paiement",
                extra={
                    "application_id": application.id,
                    "vehicle_id": vehicle.id,
                    "payment_id": dto.payment_id,
                },
            )

            # =========================
            # RESULT
            # =========================

            return CompleteRentalPaymentResult(
                application_id=application.id,
                vehicle_id=vehicle.id,
                rental_started=True,
                message="Location activée avec succès",
            )

        except Exception:

            logger.exception(
                "Erreur finalisation location",
                extra={
                    "application_id": dto.application_id,
                    "payment_id": dto.payment_id,
                },
            )

            raise