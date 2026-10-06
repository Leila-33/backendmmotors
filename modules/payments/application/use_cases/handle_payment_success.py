import logging
from datetime import datetime, timezone
from modules.applications.domain.enums import EventType
from modules.applications.domain.exceptions import ApplicationNotFound

from modules.vehicles.domain.enums import VehicleType

from modules.payments.domain.enums import PaymentStatus
from modules.payments.domain.exceptions import (
    PaymentNotFound,
    PaymentInvalid,
)

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
    """
    Traite la confirmation d'un paiement Stripe et déclenche
    la finalisation correspondante selon le type de véhicule.

    Pour une vente, le dossier et le véhicule sont finalisés ;
    pour une location, la location est activée.

    Le traitement est idempotent afin d'éviter de traiter plusieurs fois
    un même paiement confirmé par Stripe.
    """
    def __init__(
        self,
        payment_repository,
        application_repository,
        complete_sale_payment_uc,
        complete_rental_payment_uc,
        sales_dashboard_repository,
        notification_service,
        event_service,
        stripe_service,
        unit_of_work,
    ):
        self.payment_repository = payment_repository
        self.application_repository = application_repository

        self.complete_sale_payment_uc = (
            complete_sale_payment_uc
        )

        self.complete_rental_payment_uc = (
            complete_rental_payment_uc
        )

        self.sales_dashboard_repository = (
            sales_dashboard_repository
        )

        self.notification_service = notification_service
        self.event_service = event_service
        self.stripe_service = stripe_service
        self.unit_of_work = unit_of_work

    async def execute(
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
            # SAVE STRIPE INFORMATION
            # =========================

            payment.stripe_payment_intent_id = (
                dto.stripe_payment_intent_id
            )

            # =========================
            # SET DEFAULT PAYMENT METHOD
            # =========================

            if not payment.stripe_customer_id:
                raise PaymentInvalid(
                    "Customer Stripe absent du paiement."
                )

            if not dto.stripe_payment_intent_id:
                raise PaymentInvalid(
                    "PaymentIntent Stripe absent du paiement."
                )

            self.stripe_service.set_customer_default_payment_method(
                customer_id=payment.stripe_customer_id,
                payment_intent_id=dto.stripe_payment_intent_id,
            )

            # =========================
            # MARK PAYMENT AS PAID
            # =========================

            payment.status = PaymentStatus.PAID
            payment.paid_at = datetime.now(timezone.utc)

            self.payment_repository.update(
                payment
            )

            # =========================
            # ROUTAGE MÉTIER
            # =========================
            sale_result = None

            if vehicle.type == VehicleType.SALE:

                sale_result = self.complete_sale_payment_uc.execute(
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
                type=EventType.PAYMENT_SUCCEEDED,
                message="Paiement confirmé",
                application_id=application.id,
                user_id=application.user_id,
                vehicle_id=vehicle.id,
                event_metadata={
                    "payment_id": payment.id,
                    "amount": payment.amount,
                    "vehicle_type": (
                        vehicle.type.value
                    ),
                    "stripe_session_id": (
                        dto.stripe_session_id
                    ),
                    "stripe_customer_id": (
                        payment.stripe_customer_id
                    ),
                    "stripe_payment_intent_id": (
                        dto.stripe_payment_intent_id
                    ),
                },
            )

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

            # =========================
            # UPDATE MY LEADS COUNT
            # =========================

            if (
                vehicle.type == VehicleType.SALE
                and sale_result
                and sale_result.assigned_agent_id
            ):
                my_leads_count = (
                    self.sales_dashboard_repository
                    .count_my_leads(
                        agent_id=sale_result.assigned_agent_id,
                    )
                )

                await self.notification_service.send_update(
                    user_id=sale_result.assigned_agent_id,
                    payload={
                        "type": "MY_LEADS_UPDATED",
                        "count": my_leads_count,
                    },
                )

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
                    "stripe_customer_id": (
                        payment.stripe_customer_id
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