from modules.applications.domain.enums import EventType
from modules.vehicles.domain.enums import VehicleType
from modules.payments.domain.enums import PaymentStatus
from modules.payments.domain.exceptions import PaymentNotFound
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.applications.domain.enums import (
    EventType,
)

from modules.payments.api.schemas import (
    HandlePaymentSuccessResponse
)
import logging

logger = logging.getLogger(__name__)

class HandlePaymentSuccessUseCase:

    def __init__(
        self,
        payment_repository,
        application_repository,
        complete_sale_payment_uc,
        complete_rental_payment_uc,
        event_service,
        uow,
    ):

        self.payment_repository = (
            payment_repository
        )

        self.application_repository = (
            application_repository
        )

        self.complete_sale_payment_uc = (
            complete_sale_payment_uc
        )

        self.complete_rental_payment_uc = (
            complete_rental_payment_uc
        )

        self.event_service = (
            event_service
        )

        self.uow = (
            uow
        )
    def execute(
        self,
        stripe_session_id: str,
    ) -> HandlePaymentSuccessResponse:

        try:

            payment = (
                self.payment_repository
                .get_by_session_id(
                    stripe_session_id
                )
            )


            if not payment:
                raise PaymentNotFound()



            # =========================
            # IDEMPOTENCY
            # =========================

            if payment.status == PaymentStatus.PAID:

                application = (
                    self.application_repository
                    .get_by_id(
                        payment.application_id
                    )
                )
                logger.info(
        "Webhook Stripe déjà traité",
        extra={
            "payment_id": payment.id,
            "stripe_session_id": stripe_session_id,
        }
    )
                return HandlePaymentSuccessResponse(

                    payment_id=payment.id,

                    status=payment.status.value,

                    vehicle_type=(
                        application.vehicle.type.value
                    ),

                    application_id=(
                        application.id
                    ),

                    message=(
                        "Paiement déjà traité"
                    )
                )



            payment.status = (
                PaymentStatus.PAID
            )


            self.payment_repository.update(
                payment
            )



            application = (
                self.application_repository
                .get_by_id(
                    payment.application_id
                )
            )


            if not application:
                raise ApplicationNotFound()



            vehicle = application.vehicle



            # =========================
            # ROUTAGE METIER
            # =========================

            if vehicle.type == VehicleType.SALE:

                self.complete_sale_payment_uc.execute(
                    application,
                    payment,
                )


            elif vehicle.type == VehicleType.RENT:

                self.complete_rental_payment_uc.execute(
                    application,
                    payment,
                )



            self.event_service.log(
                type=EventType.PAYMENT_SUCCESS,
                application_id=application.id,
                user_id=application.user_id,
                message="Paiement confirmé",
                event_metadata={
                    "payment_id": payment.id,
                    "amount": payment.amount,
                    "vehicle_type": vehicle.type.value,
                }
            )



            self.uow.commit()


            logger.info(
                "Paiement Stripe traité avec succès",
                extra={
                    "payment_id": payment.id,
                    "stripe_session_id": stripe_session_id,
                    "application_id": application.id,
                    "vehicle_id": vehicle.id,
                }
            )


            return HandlePaymentSuccessResponse(
                payment_id=payment.id,
                status=payment.status.value,
                vehicle_type=vehicle.type.value,
                application_id=application.id,
                message="Paiement traité avec succès"
            )


        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur traitement paiement Stripe",
                extra={
                    "stripe_session_id": stripe_session_id,
                    "payment_id": (
                        payment.id
                        if payment
                        else None
                    ),
                }
            )

            raise