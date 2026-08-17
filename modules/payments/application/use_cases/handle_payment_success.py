import logging

from modules.applications.domain.enums import EventType
from modules.applications.domain.exceptions import ApplicationNotFound

from modules.vehicles.domain.enums import VehicleType

from modules.payments.domain.enums import PaymentStatus
from modules.payments.domain.exceptions import PaymentNotFound

from modules.payments.application.dtos.complete_sale_payment_dto import (
    CompleteSalePaymentDTO,
)
from modules.payments.application.dtos.complete_rental_payment_dto import (
    CompleteRentalPaymentDTO,
)
from modules.payments.application.dtos.handle_payment_success_dto import HandlePaymentSuccessDTO
from modules.payments.application.results.handle_payment_success_result import (
    HandlePaymentSuccessResult,
)


logger = logging.getLogger(__name__)


class HandlePaymentSuccessUseCase:

    def __init__(
        self,
        payment_repository,
        application_repository,
        complete_sale_payment_uc,
        complete_rental_payment_uc,
        event_service,
        unit_of_work,
    ):
        self.payment_repository = payment_repository
        self.application_repository = (
            application_repository
        )

        self.complete_sale_payment_uc = (
            complete_sale_payment_uc
        )

        self.complete_rental_payment_uc = (
            complete_rental_payment_uc
        )

        self.event_service = event_service
        self.unit_of_work = unit_of_work

    def execute(
        self,
        dto: HandlePaymentSuccessDTO,
    ):

        payment = None

        try:

            # =========================
            # GET PAYMENT
            # =========================

            payment = (
                self.payment_repository
                .get_by_session_id(
                    dto.stripe_session_id
                )
            )

            if payment is None:
                raise PaymentNotFound()

            # =========================
            # GET APPLICATION
            # =========================

            application = (
                self.application_repository
                .get_by_id(
                    payment.application_id
                )
            )

            if application is None:
                raise ApplicationNotFound()

            vehicle = application.vehicle

            # =========================
            # IDEMPOTENCY
            # =========================

            if payment.status == PaymentStatus.PAID:

                logger.info(
                    "Webhook Stripe déjà traité",
                    extra={
                        "payment_id": payment.id,
                        "stripe_session_id": (
                            dto.stripe_session_id
                        ),
                        "application_id": application.id,
                    },
                )

                return HandlePaymentSuccessResult(
                    payment_id=payment.id,
                    status=payment.status.value,
                    vehicle_type=vehicle.type.value,
                    application_id=application.id,
                    message="Paiement déjà traité",
                )

            # =========================
            # MARK PAYMENT AS PAID
            # =========================

            payment.status = PaymentStatus.PAID

            self.payment_repository.update(
                payment
            )

            # =========================
            # ROUTAGE MÉTIER
            # =========================

            if vehicle.type == VehicleType.SALE:

                self.complete_sale_payment_uc.execute(

                    CompleteSalePaymentDTO(
                        application_id=application.id,
                        payment_id=payment.id,
                    )
                )

            elif vehicle.type == VehicleType.RENT:

                self.complete_rental_payment_uc.execute(

                    CompleteRentalPaymentDTO(
                        application_id=application.id,
                        payment_id=payment.id,
                    )
                )


            # =========================
            # PAYMENT SUCCESS EVENT
            # =========================

            self.event_service.log(

                type=EventType.PAYMENT_SUCCESS,

                application_id=application.id,

                user_id=application.user_id,

                vehicle_id=vehicle.id,

                message="Paiement confirmé",

                event_metadata={
                    "payment_id": payment.id,
                    "amount": payment.amount,
                    "vehicle_type": (
                        vehicle.type.value
                    ),
                },
            )

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

            # =========================
            # SUCCESS LOG
            # =========================

            logger.info(
                "Paiement Stripe traité avec succès",
                extra={
                    "payment_id": payment.id,
                    "stripe_session_id": (
                        dto.stripe_session_id
                    ),
                    "application_id": application.id,
                    "vehicle_id": vehicle.id,
                },
            )

            # =========================
            # RESULT
            # =========================

            return HandlePaymentSuccessResult(

                payment_id=payment.id,

                status=payment.status.value,

                vehicle_type=vehicle.type.value,

                application_id=application.id,

                message="Paiement traité avec succès",
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur traitement paiement Stripe",
                extra={
                    "stripe_session_id": (
                        dto.stripe_session_id
                    ),
                    "payment_id": (
                        payment.id
                        if payment
                        else None
                    ),
                },
            )

            raise