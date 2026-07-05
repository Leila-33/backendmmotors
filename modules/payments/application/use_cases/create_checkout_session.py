from uuid import uuid4

from modules.payments.domain.entities.payment import Payment
from modules.core.enums import PaymentStatus
from core.config import settings

from modules.core.exceptions import ApplicationNotFound, PaymentNotAllowed
from modules.core.enums import ApplicationStatus, EventType
from modules.applications.domain.entities.event import Event

from uuid import uuid4


class CreateCheckoutSessionUseCase:

    def __init__(
        self,
        payment_repository,
        stripe_service,
        application_repository,
        event_repository
    ):
        self.payment_repository = payment_repository
        self.stripe_service = stripe_service
        self.application_repository = application_repository
        self.event_repository = event_repository

    # =========================
    # EXECUTE
    # =========================
    def execute(self, dto):

        application = self.application_repository.get_by_id(dto.application_id)

        if not application:
            raise ApplicationNotFound()

        if application.status != ApplicationStatus.APPROVED:
            raise PaymentNotAllowed()

        existing_payment = self.payment_repository.get_by_application_id(
            dto.application_id
        )

        payment = None

        # =========================
        # HANDLE EXISTING PAYMENT
        # =========================
        if existing_payment:

            if existing_payment.status == PaymentStatus.PAID:
                return {
                    "checkout_url": None,
                    "payment_id": existing_payment.id
                }

            if existing_payment.status == PaymentStatus.PENDING:
                # ❌ on ne réutilise PAS Stripe session
                # 👉 on recrée une session pour garantir validité
                session = self.stripe_service.create_checkout_session(
                    application_id=dto.application_id,
                    amount=dto.amount,
                    product_name=dto.product_name,
                    success_url=settings.SUCCESS_URL,
                    cancel_url=settings.CANCEL_URL,
                    customer_email=dto.email
                )

                # update session id
                existing_payment.stripe_session_id = session.id
                self.payment_repository.update(existing_payment)
                self.payment_repository.commit()

                return {
                    "checkout_url": session.url,
                    "payment_id": existing_payment.id
                }

            if existing_payment.status == PaymentStatus.FAILED:
                payment = existing_payment

        # =========================
        # CREATE NEW STRIPE SESSION
        # =========================
        session = self.stripe_service.create_checkout_session(
            application_id=dto.application_id,
            amount=dto.amount,
            product_name=dto.product_name,
            success_url=settings.SUCCESS_URL,
            cancel_url=settings.CANCEL_URL,
            customer_email=dto.email
        )

        # =========================
        # CREATE PAYMENT
        # =========================
        if not payment:

            payment = Payment(
                id=str(uuid4()),
                application_id=dto.application_id,
                user_id=dto.user_id,
                stripe_session_id=session.id,
                amount=dto.amount,
                status=PaymentStatus.PENDING,
                description=dto.product_name
            )

            self.payment_repository.save(payment)

        else:

            payment.stripe_session_id = session.id
            payment.status = PaymentStatus.PENDING
            self.payment_repository.update(payment)

        self.payment_repository.commit()

        # =========================
        # EVENT
        # =========================
        self.event_repository.save(
            Event(
                id=str(uuid4()),
                application_id=application.id,
                user_id=dto.user_id,
                type=EventType.PAYMENT_INITIATED,
                message="Paiement initialisé",
                event_metadata={
                    "amount": dto.amount,
                    "stripe_session_id": session.id
                }
            )
        )

        self.event_repository.commit()

        # =========================
        # RETURN
        # =========================
        return {
            "checkout_url": session.url,
            "payment_id": payment.id
        }