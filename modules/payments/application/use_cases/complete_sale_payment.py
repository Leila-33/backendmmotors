import logging

from modules.applications.domain.enums import (
    ApplicationStatus,
    EventType,
)
from modules.vehicles.domain.enums import VehicleStatus
from modules.leads.domain.enums import LeadStatus

from modules.applications.domain.exceptions import (
    ApplicationNotFound,
)

from modules.payments.application.dtos.complete_sale_payment_dto import (
    CompleteSalePaymentDTO,
)
from modules.payments.application.results.complete_sale_payment_result import (
    CompleteSalePaymentResult,
)

from modules.warranties.application.dtos.activate_vehicle_warranty_dto import (
    ActivateVehicleWarrantyDTO,
)

from modules.financing.application.dtos.create_financing_contract_dto import (
    CreateFinancingContractDTO,
)

from modules.payments.application.dtos.create_subscription_dto import (
    CreateSubscriptionDTO,
)

from modules.financing.application.dtos.create_installments_dto import (
    CreateInstallmentsDTO,
)

from modules.payments.domain.exceptions import (
    PaymentNotFound,
)

logger = logging.getLogger(__name__)


class CompleteSalePaymentUseCase:
    """
    Finalise le paiement d'une vente en marquant le véhicule comme vendu,
    en mettant à jour le dossier et en activant sa garantie.

    Lorsque la vente est financée, le contrat de financement,
    l'abonnement Stripe et les échéances de paiement sont également créés.
    """
    def __init__(
        self,
        vehicle_repository,
        application_repository,
        payment_repository,
        lead_repository,
        event_service,
        activate_vehicle_warranty_uc,
        create_financing_contract_uc,
        create_subscription_uc,
        create_installments_uc,
    ):
        self.vehicle_repository = vehicle_repository
        self.application_repository = (
            application_repository
        )
        self.payment_repository = (
            payment_repository
        )
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
        dto: CompleteSalePaymentDTO,
    ):

        try:

            # =========================
            # GET APPLICATION
            # =========================

            application = (
                self.application_repository
                .get_by_id(
                    dto.application_id
                )
            )

            if application is None:
                raise ApplicationNotFound()

            vehicle = application.vehicle

            # =========================
            # GET PAYMENT
            # =========================

            payment = (
                self.payment_repository
                .get_by_id(
                    dto.payment_id
                )
            )

            if payment is None:
                raise PaymentNotFound()

            # =========================
            # IDEMPOTENCE
            # =========================

            if (
                application.status
                == ApplicationStatus.COMPLETED
            ):
                return CompleteSalePaymentResult(
                    application_id=application.id,
                    vehicle_id=vehicle.id,
                    warranty_created=True,
                    financing_created=(
                        application.financing is not None
                    ),
                    assigned_agent_id=None,
                    message="Vente déjà finalisée",
                )

            # =========================
            # VEHICLE SOLD
            # =========================

            vehicle.status = VehicleStatus.SOLD
            vehicle.is_available = False

            self.vehicle_repository.update(
                vehicle
            )

            # =========================
            # APPLICATION STATUS
            # =========================

            is_financed = (
                application.financing
                and
                application.financing.financed_amount > 0
            )

            if is_financed:
                application.status = (
                    ApplicationStatus.PAID
                )
            else:
                application.status = (
                    ApplicationStatus.COMPLETED
                )

            self.application_repository.update(
                application
            )

            # =========================
            # PAYMENT EVENT
            # =========================

            self.event_service.log(
                type=EventType.DEPOSIT_PAID,
                application_id=application.id,
                vehicle_id=vehicle.id,
                user_id=application.user_id,
                message="Acompte véhicule payé.",
                event_metadata={
                    "payment_id": dto.payment_id,
                    "vehicle_id": vehicle.id,
                },
            )

            # =========================
            # LEAD WON
            # =========================
            assigned_agent_id = None

            if application.quote_id:

                lead = (
                    self.lead_repository
                    .get_by_quote_id(
                        application.quote_id
                    )
                )

                if lead:
                    assigned_agent_id = lead.assigned_to

                    lead.status = LeadStatus.WON

                    self.lead_repository.update(
                        lead
                    )

                    self.event_service.log(
                        type=EventType.LEAD_WON,
                        application_id=application.id,
                        vehicle_id=vehicle.id,
                        quote_id=application.quote_id,
                        lead_id=lead.id,
                        user_id=lead.assigned_to,
                        message=(
                            "Lead converti après paiement"
                        ),
                        event_metadata={
                            "lead_id": lead.id,
                            "quote_id": (
                                application.quote_id
                            ),
                        },
                    )

            # =========================
            # WARRANTY
            # =========================

            self.activate_vehicle_warranty_uc.execute(
                ActivateVehicleWarrantyDTO(
                    vehicle_id=vehicle.id,
                    mileage=vehicle.mileage,
                    user_id=application.user_id,
                )
            )

            # =========================
            # FINANCING
            # =========================

            financing_created = False

            if is_financed:

                # =========================
                # FINANCING CONTRACT
                # =========================

                contract_result = (
                    self.create_financing_contract_uc
                    .execute(
                        CreateFinancingContractDTO(
                            application_id=application.id,
                        )
                    )
                )

                # =========================
                # SUBSCRIPTION
                # =========================

                self.create_subscription_uc.execute(
                    CreateSubscriptionDTO(
                        contract_id=(
                            contract_result.contract_id
                        ),
                        stripe_customer_id=(
                            payment.stripe_customer_id
                        ),
                        user_id=application.user_id,
                    )
                )

                # =========================
                # INSTALLMENTS
                # =========================

                self.create_installments_uc.execute(
                    CreateInstallmentsDTO(
                        contract_id=(
                            contract_result.contract_id
                        ),
                    )
                )

                financing_created = True

            # =========================
            # SUCCESS LOG
            # =========================

            logger.info(
                "Vente finalisée après paiement",
                extra={
                    "application_id": application.id,
                    "vehicle_id": vehicle.id,
                    "payment_id": dto.payment_id,
                    "financing_created": (
                        financing_created
                    ),
                },
            )

            # =========================
            # RESULT
            # =========================

            return CompleteSalePaymentResult(
                application_id=application.id,
                vehicle_id=vehicle.id,
                warranty_created=True,
                financing_created=(
                    financing_created
                ),
                assigned_agent_id=assigned_agent_id,
                message=(
                    "Vente finalisée avec succès"
                ),
            )

        except Exception:

            logger.exception(
                "Erreur finalisation vente",
                extra={
                    "application_id": (
                        dto.application_id
                    ),
                    "payment_id": (
                        dto.payment_id
                    ),
                },
            )

            raise

