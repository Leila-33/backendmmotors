import logging
from datetime import datetime, timezone
from uuid import uuid4

from modules.payments.domain.entities.payment import Payment
from modules.payments.domain.enums import PaymentStatus
from modules.payments.domain.exceptions import PaymentNotAllowed

from modules.applications.domain.exceptions import (
    ApplicationNotFound,
)

from modules.applications.domain.enums import (
    ApplicationStatus,
    EventType,
)

from core.config.settings import settings

from modules.payments.application.results.create_checkout_session_result import (
    CreateCheckoutSessionResult,
)
from modules.payments.application.dtos.create_checkout_session_dto import (
    CreateCheckoutSessionDTO
)

logger = logging.getLogger(__name__)


class CreateCheckoutSessionUseCase:

    def __init__(
        self,
        payment_repository,
        stripe_service,
        application_repository,
        event_service,
        unit_of_work,
    ):
        self.payment_repository = payment_repository
        self.stripe_service = stripe_service
        self.application_repository = application_repository
        self.event_service = event_service
        self.unit_of_work = unit_of_work

    def execute(
        self,
        dto: CreateCheckoutSessionDTO,
    ):

        try:

            # =========================
            # APPLICATION
            # =========================

            application = (
                self.application_repository
                .get_by_id(
                    dto.application_id
                )
            )

            if application is None:
                raise ApplicationNotFound()

            if (
                application.status
                != ApplicationStatus.APPROVED
            ):
                raise PaymentNotAllowed()

            # =========================
            # ALREADY PAID
            # =========================

            payment = (
                self.payment_repository
                .get_by_application_and_status(
                    application.id,
                    PaymentStatus.PAID,
                )
            )

            if payment:

                logger.info(
                    "Paiement déjà effectué",
                    extra={
                        "application_id": application.id,
                        "payment_id": payment.id,
                    },
                )

                return CreateCheckoutSessionResult(
                    checkout_url=None,
                    payment_id=payment.id,
                )

            # =========================
            # PENDING PAYMENT
            # =========================

            payment = (
                self.payment_repository
                .get_by_application_and_status(
                    application.id,
                    PaymentStatus.PENDING,
                )
            )

            # =========================
            # FAILED PAYMENT
            # =========================

            if payment is None:

                payment = (
                    self.payment_repository
                    .get_by_application_and_status(
                        application.id,
                        PaymentStatus.FAILED,
                    )
                )

            # =========================
            # STRIPE SESSION
            # =========================

            session = (
                self.stripe_service
                .create_checkout_session(
                    application_id=application.id,
                    amount=dto.amount,
                    product_name=dto.product_name,
                    success_url=settings.SUCCESS_URL,
                    cancel_url=settings.CANCEL_URL,
                    customer_email=dto.email,
                )
            )

            # =========================
            # CREATE PAYMENT
            # =========================

            if payment is None:

                payment = Payment(
                    id=str(uuid4()),
                    application_id=application.id,
                    user_id=dto.user_id,
                    amount=dto.amount,
                    currency="eur",
                    stripe_session_id=session.id,
                    status=PaymentStatus.PENDING,
                    description=dto.product_name,
                    created_at=datetime.now(
                        timezone.utc
                    ),
                )

                self.payment_repository.save(
                    payment
                )

            # =========================
            # REUSE PAYMENT
            # =========================

            else:

                payment.stripe_session_id = (
                    session.id
                )

                payment.status = (
                    PaymentStatus.PENDING
                )

                self.payment_repository.update(
                    payment
                )

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                type=EventType.PAYMENT_INITIATED,
                message="Paiement initialisé",
                user_id=dto.user_id,
                application_id=application.id,
                vehicle_id=application.vehicle_id,
                event_metadata={
                    "payment_id": payment.id,
                    "amount": payment.amount,
                    "stripe_session_id": session.id,
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
                "Session checkout Stripe créée",
                extra={
                    "application_id": application.id,
                    "payment_id": payment.id,
                    "stripe_session_id": session.id,
                },
            )

            # =========================
            # RESULT
            # =========================

            return CreateCheckoutSessionResult(
                checkout_url=session.url,
                payment_id=payment.id,
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur création session checkout Stripe",
                extra={
                    "application_id": (
                        dto.application_id
                    ),
                    "user_id": dto.user_id,
                },
            )

            raise