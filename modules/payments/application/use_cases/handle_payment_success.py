from modules.applications.domain.enums import ApplicationStatus, EventType
from modules.vehicles.domain.enums import VehicleStatus, VehicleType
from modules.payments.domain.enums import PaymentStatus
from modules.payments.domain.exceptions import PaymentNotFound
from modules.applications.domain.entities.event import Event
from uuid import uuid4
from modules.applications.domain.exceptions import ApplicationNotFound

from uuid import uuid4
from datetime import datetime, timezone

from modules.payments.domain.enums import PaymentStatus
from modules.applications.domain.enums import (
    ApplicationStatus,
    EventType,
)
from modules.vehicles.domain.enums import VehicleStatus
from modules.leads.domain.enums import LeadStatus

from modules.payments.api.schemas import (
    HandlePaymentSuccessResponseDTO
)

from modules.applications.domain.entities.event import Event

from modules.payments.domain.exceptions import PaymentNotFound
from modules.applications.domain.exceptions import ApplicationNotFound


class HandlePaymentSuccessUseCase:

    def __init__(
        self,
        payment_repository,
        vehicle_repository,
        application_repository,
        warranty_repository,
        event_repository,
        lead_repository,
        activate_vehicle_warranty_uc,
        uow,
        create_financing_contract_uc=None,
        create_subscription_uc=None,
        create_installments_uc=None,
    ):

        self.payment_repository = payment_repository
        self.vehicle_repository = vehicle_repository
        self.application_repository = application_repository
        self.warranty_repository = warranty_repository
        self.event_repository = event_repository
        self.lead_repository = lead_repository

        self.activate_vehicle_warranty_uc = (
            activate_vehicle_warranty_uc
        )

        self.create_financing_contract_uc = (
            create_financing_contract_uc
        )

        self.create_subscription_uc = (
            create_subscription_uc
        )

        self.create_installments_uc = (
            create_installments_uc
        )

        self.uow = uow


    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(
        self,
        stripe_session_id: str
    ):
        try:
            # =================================================
            # PAYMENT
            # =================================================

            payment = (
                self.payment_repository
                .get_by_session_id(
                    stripe_session_id
                )
            )


            if not payment:
                raise PaymentNotFound()


            # =================================================
            # IDEMPOTENCY WEBHOOK
            # =================================================

            if payment.status == PaymentStatus.PAID:

                return HandlePaymentSuccessResponseDTO(

                    payment_id=payment.id,

                    status=payment.status.value
                )


            payment.status = PaymentStatus.PAID

            self.payment_repository.update(
                payment
            )


            # =================================================
            # APPLICATION
            # =================================================

            application = (
                self.application_repository
                .get_by_id(
                    payment.application_id
                )
            )


            if not application:
                raise ApplicationNotFound()


            vehicle = application.vehicle


            # =================================================
            # VEHICLE
            # =================================================

            vehicle.status = VehicleStatus.SOLD

            vehicle.is_available = False

            self.vehicle_repository.update(
                vehicle
            )


            # =================================================
            # APPLICATION STATUS
            # =================================================

            financing = application.financing


            is_cash_payment = (
                not financing
                or financing.financed_amount == 0
            )


            if is_cash_payment:

                application.status = (
                    ApplicationStatus.COMPLETED
                )

            else:

                application.status = (
                    ApplicationStatus.PAID
                )


            self.application_repository.update(
                application
            )


            # =================================================
            # LEAD WON
            # =================================================

            if application.quote:

                lead = application.quote.lead

                if lead:

                    lead.status = LeadStatus.WON

                    self.lead_repository.update(
                        lead
                    )


                    self.event_repository.save(
                        Event(
                            id=str(uuid4()),

                            application_id=application.id,

                            user_id=lead.assigned_to,

                            type=EventType.LEAD_WON,

                            message=(
                                "Lead converti après paiement."
                            ),

                            event_metadata={
                                "lead_id": lead.id,
                                "quote_id": application.quote.id,
                            },

                            created_at=datetime.now(
                                timezone.utc
                            )
                        )
                    )


            # =================================================
            # WARRANTY
            # =================================================

            warranty = (
                self.activate_vehicle_warranty_uc.execute(
                    vehicle=vehicle,
                    mileage=vehicle.mileage
                )
            )


            self.warranty_repository.update(
                warranty
            )


            self.event_repository.save(
                Event(
                    id=str(uuid4()),

                    application_id=application.id,

                    user_id=application.user_id,

                    type=EventType.WARRANTY_ACTIVATED,

                    message="Garantie activée.",

                    event_metadata={
                        "warranty_id": warranty.id
                    },

                    created_at=datetime.now(
                        timezone.utc
                    )
                )
            )


            # =================================================
            # PAYMENT EVENT
            # =================================================

            self.event_repository.save(
                Event(
                    id=str(uuid4()),

                    application_id=application.id,

                    user_id=application.user_id,

                    type=EventType.DEPOSIT_PAID,

                    message=(
                        f"Acompte de "
                        f"{payment.amount:.2f} € payé."
                    ),

                    event_metadata={
                        "payment_id": payment.id,
                        "amount": payment.amount,
                        "stripe_session_id": stripe_session_id
                    },

                    created_at=datetime.now(
                        timezone.utc
                    )
                )
            )


            # =================================================
            # FINANCING
            # =================================================

            if (
                application.financing
                and application.financing.financed_amount > 0
                and not application.financing_contract
                and self.create_financing_contract_uc
            ):

                contract = (
                    self.create_financing_contract_uc.execute(
                        application_id=application.id
                    )
                )


                if self.create_subscription_uc:

                    self.create_subscription_uc.execute(
                        contract=contract,
                        customer_email=application.email,
                        customer_name=(
                            f"{application.first_name} "
                            f"{application.last_name}"
                        ),
                        user_id=application.user_id
                    )


                if self.create_installments_uc:

                    self.create_installments_uc.execute(
                        contract_id=contract.id
                    )


            # =================================================
            # COMMIT
            # =================================================

            self.uow.commit()


            return HandlePaymentSuccessResponseDTO(

                payment_id=payment.id,

                status=payment.status.value
            )

        except Exception:
            self.uow.rollback()
            raise