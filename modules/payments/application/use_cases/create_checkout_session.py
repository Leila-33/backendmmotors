from uuid import uuid4
from modules.payments.domain.entities.payment import Payment
from core.config.settings import settings
from modules.payments.domain.exceptions import PaymentNotAllowed
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.payments.domain.enums import PaymentStatus
from modules.applications.domain.enums import ApplicationStatus, EventType
from modules.applications.domain.entities.event import Event
from datetime import datetime, timezone
from modules.payments.api.schemas import (
    CreateCheckoutSessionResponse,
)



class CreateCheckoutSessionUseCase:


    def __init__(
        self,
        payment_repository,
        stripe_service,
        application_repository,
        event_repository,
        uow,
    ):

        self.payment_repository = payment_repository
        self.stripe_service = stripe_service
        self.application_repository = application_repository
        self.event_repository = event_repository
        self.uow = uow



    def execute(
        self,
        dto
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

            if not application:
                raise ApplicationNotFound()



            if application.status != ApplicationStatus.APPROVED:
                raise PaymentNotAllowed()



            # =========================
            # ALREADY PAID
            # =========================

            payment = (
                self.payment_repository
                .get_by_application_and_status(
                    application.id,
                    PaymentStatus.PAID
                )
            )


            if payment:

                return CreateCheckoutSessionResponse(
                    checkout_url=None,
                    payment_id=payment.id
                )



            # =========================
            # PENDING PAYMENT
            # =========================

            payment = (
                self.payment_repository
                .get_by_application_and_status(
                    application.id,
                    PaymentStatus.PENDING
                )
            )



            # =========================
            # FAILED PAYMENT
            # =========================

            if not payment:

                payment = (
                    self.payment_repository
                    .get_by_application_and_status(
                        application.id,
                        PaymentStatus.FAILED
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

            if not payment:


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
                    )
                )


                self.payment_repository.save(
                    payment
                )


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

            self.event_repository.save(
                Event(

                    id=str(uuid4()),

                    application_id=application.id,

                    user_id=dto.user_id,

                    type=EventType.PAYMENT_INITIATED,

                    message="Paiement initialisé.",

                    event_metadata={

                        "payment_id": payment.id,

                        "amount": payment.amount,

                        "stripe_session_id": session.id,

                    },

                    created_at=datetime.now(
                        timezone.utc
                    )
                )
            )


            # =========================
            # COMMIT
            # =========================

            self.uow.commit()



            return CreateCheckoutSessionResponse(

                checkout_url=session.url,

                payment_id=payment.id

            )
        except Exception:
            self.uow.rollback()
            raise