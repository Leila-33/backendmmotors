from modules.applications.domain.enums import ApplicationStatus, EventType
from modules.vehicles.domain.enums import VehicleStatus
from modules.applications.domain.enums import (
    EventType,
)
from modules.vehicles.domain.enums import VehicleStatus
from modules.leads.domain.enums import LeadStatus

from modules.applications.domain.enums import (
    EventType
)
from modules.payments.api.schemas import (
    CompleteSalePaymentResponse
)
import logging

logger = logging.getLogger(__name__)

class CompleteSalePaymentUseCase:


    def __init__(
        self,
        vehicle_repository,
        application_repository,
        lead_repository,
        event_service,
        activate_vehicle_warranty_uc,
        create_financing_contract_uc,
        create_subscription_uc,
        create_installments_uc,
    ):

        self.vehicle_repository = vehicle_repository
        self.application_repository = application_repository
        self.lead_repository = lead_repository

        self.event_service = event_service

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

    def execute(
    self,
    application,
    payment,
):

        try:

            vehicle = application.vehicle


            # =========================
            # VEHICLE SOLD
            # =========================

            vehicle.status = VehicleStatus.SOLD
            vehicle.is_available = False

            self.vehicle_repository.update(
                vehicle
            )


            # =========================
            # APPLICATION
            # =========================

            if (
                application.financing
                and application.financing.financed_amount > 0
            ):
                application.status = ApplicationStatus.PAID

            else:
                application.status = ApplicationStatus.COMPLETED


            self.application_repository.update(
                application
            )


            # =========================
            # PAYMENT EVENT
            # =========================

            self.event_service.log(

                type=EventType.DEPOSIT_PAID,

                application_id=application.id,

                user_id=application.user_id,

                message="Acompte véhicule payé.",

                event_metadata={
                    "payment_id": payment.id,
                    "amount": payment.amount,
                    "vehicle_id": vehicle.id,
                },
            )


            # =========================
            # LEAD WON
            # =========================

            if application.quote:

                lead = application.quote.lead

                if lead:

                    lead.status = LeadStatus.WON

                    self.lead_repository.update(
                        lead
                    )


                    self.event_service.log(
                        type=EventType.LEAD_WON,

                        application_id=application.id,

                        user_id=lead.assigned_to,

                        message=(
                            "Lead converti après paiement"
                        ),

                        event_metadata={
                            "lead_id": lead.id,
                            "quote_id": application.quote.id,
                        },
                    )


            # =========================
            # WARRANTY
            # =========================

            self.activate_vehicle_warranty_uc.execute(
                vehicle=vehicle,
                mileage=vehicle.mileage,
                user_id=application.user_id,
            )


            # =========================
            # FINANCING
            # =========================

            if (
                application.financing
                and application.financing.financed_amount > 0
            ):

                contract = (
                    self.create_financing_contract_uc.execute(
                        application_id=application.id
                    )
                )


                self.create_subscription_uc.execute(
                    contract=contract,
                    customer_email=application.email,
                    customer_name=(
                        f"{application.first_name} "
                        f"{application.last_name}"
                    ),
                    user_id=application.user_id,
                )


                self.create_installments_uc.execute(
                    contract_id=contract.id
                )


            return CompleteSalePaymentResponse(

                application_id=application.id,

                vehicle_id=vehicle.id,

                warranty_created=True,

                financing_created=(
                    application.financing is not None
                ),

                message=(
                    "Vente finalisée avec succès"
                ),
            )


        except Exception:

            logger.exception(
                "Erreur finalisation vente",
                extra={
                    "application_id": application.id,
                    "payment_id": payment.id,
                },
            )

            raise