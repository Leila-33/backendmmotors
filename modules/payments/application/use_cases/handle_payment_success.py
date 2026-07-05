from modules.core.enums import PaymentStatus, ApplicationStatus, VehicleStatus, VehicleType, EventType
from modules.core.exceptions import PaymentNotFound, ApplicationNotFound
from modules.applications.domain.entities.event import Event
from uuid import uuid4

class HandlePaymentSuccessUseCase:

    def __init__(
        self,
        payment_repository,
        vehicle_repository,
        application_repository,
        warranty_repository,
        event_repository,
        activate_vehicle_warranty_uc,
        create_financing_contract_uc=None,
        create_subscription_uc=None,
        create_installments_uc=None
    ):

        self.payment_repository = payment_repository
        self.vehicle_repository = vehicle_repository
        self.application_repository = application_repository
        self.warranty_repository = warranty_repository
        self.event_repository = event_repository

        self.activate_vehicle_warranty_uc = activate_vehicle_warranty_uc

        self.create_financing_contract_uc = create_financing_contract_uc
        self.create_subscription_uc = create_subscription_uc
        self.create_installments_uc = create_installments_uc

    # =========================
    # EXECUTE
    # =========================
    def execute(
        self,
        stripe_session_id: str
    ):
        # =========================
        # PAYMENT
        # =========================
        payment = (
            self.payment_repository
            .get_by_session_id(
                stripe_session_id
            )
        )

        if not payment:
            raise PaymentNotFound()

        # =========================
        # WEBHOOK IDEMPOTENCY
        # =========================
        if payment.status == PaymentStatus.PAID:

            return {
                "payment_id": payment.id,
                "status": "PAID"
            }

        payment.status = PaymentStatus.PAID

        self.payment_repository.update(payment)


        # =========================
        # APPLICATION
        # =========================
        application = (
            self.application_repository
            .get_by_id(
                payment.application_id
            )
        )

        if not application:
            raise ApplicationNotFound()
        
        vehicle = application.vehicle
        vehicle.status = VehicleStatus.SOLD
        vehicle.is_available = False

        self.vehicle_repository.update(vehicle)

        # =========================
        # EVENT
        # =========================

        financing = application.financing

        is_cash_payment = (
            not financing
            or financing.financed_amount == 0
        )

        if vehicle.type == VehicleType.SALE:

            if is_cash_payment:
                application.status = ApplicationStatus.COMPLETED
            else:
                application.status = ApplicationStatus.PAID

            event_type = EventType.DEPOSIT_PAID

            message = (
                f"Acompte de {payment.amount:.2f} € payé."
            )

            # =========================
            # WARRANTY ACTIVATION
            # =========================
            warranty = self.activate_vehicle_warranty_uc.execute(
                vehicle=vehicle,
                mileage=vehicle.mileage
            )
            self.warranty_repository.update(warranty)
            self.event_repository.save(
                Event(
                    id=str(uuid4()),
                    application_id=application.id,
                    user_id=application.user_id,
                    type=EventType.WARRANTY_CREATED,
                    message="Garantie activée.",
                    event_metadata={
                        "warranty_id": warranty.id,
                        "start_date": str(warranty.start_date),
                        "end_date": str(warranty.end_date)
                    }
                )
            )

        else:

            event_type = (
                EventType.RENTAL_PAYMENT_PAID
            )

            message = (
                f"Paiement de réservation de "
                f"{payment.amount:.2f} € reçu."
            )

        self.event_repository.save(
            Event(
                id=str(uuid4()),
                application_id=application.id,
                user_id=application.user_id,
                type=event_type,
                message=message,
                event_metadata={
                    "payment_id": payment.id,
                    "amount": payment.amount
                }
            )
        )


        # =========================
        # FINANCING
        # =========================

        # création du contrat uniquement si financement
        if (
            vehicle.type == VehicleType.SALE
            and not application.financing_contract
            and self.create_financing_contract_uc
            and financing
            and financing.financed_amount > 0
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

        # =========================
        # COMMIT
        # =========================
        self.payment_repository.commit()

        return {
            "payment_id": payment.id,
            "status": "PAID"
        }