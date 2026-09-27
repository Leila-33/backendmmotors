import logging

from modules.applications.domain.exceptions import (
    ApplicationNotFound,
)

from modules.financing.domain.exceptions import (
    FinancingContractNotFound,
)

from modules.applications.domain.enums import (
    EventType,
)

from modules.payments.domain.subscription_status_mapper import (
    SubscriptionStatusMapper,
)
from modules.payments.application.dtos.create_subscription_dto import (
    CreateSubscriptionDTO
)
from modules.payments.application.results.create_subscription_result import (
    CreateSubscriptionResult,
)


logger = logging.getLogger(__name__)


class CreateSubscriptionUseCase:
    """
    Crée l'abonnement Stripe associé à un contrat de financement
    et enregistre ses informations dans le contrat.

    Le traitement est idempotent afin d'éviter la création
    de plusieurs abonnements pour un même contrat.
    """
    def __init__(
        self,
        stripe_service,
        financing_contract_repository,
        application_repository,
        event_service,
    ):
        self.stripe_service = stripe_service

        self.financing_contract_repository = (
            financing_contract_repository
        )

        self.application_repository = (
            application_repository
        )

        self.event_service = event_service

    def execute(
        self,
        dto: CreateSubscriptionDTO,
    ):

        contract = None

        try:

            # =========================
            # CONTRACT
            # =========================

            contract = (
                self.financing_contract_repository
                .find_by_id(
                    dto.contract_id
                )
            )

            if contract is None:
                raise FinancingContractNotFound()

            # =========================
            # IDEMPOTENCE
            # =========================

            if contract.stripe_subscription_id:

                logger.info(
                    "Abonnement Stripe déjà existant",
                    extra={
                        "contract_id": contract.id,
                        "stripe_subscription_id": (
                            contract.stripe_subscription_id
                        ),
                        "user_id": dto.user_id,
                    },
                )

                return CreateSubscriptionResult(
                    contract_id=contract.id,
                    stripe_customer_id=(
                        contract.stripe_customer_id
                    ),
                    stripe_subscription_id=(
                        contract.stripe_subscription_id
                    ),
                    subscription_status=(
                        contract.subscription_status.value
                        if contract.subscription_status
                        else None
                    ),
                )

            # =========================
            # APPLICATION
            # =========================

            application = (
                self.application_repository
                .get_by_id(
                    contract.application_id
                )
            )

            if application is None:
                raise ApplicationNotFound()


            # =========================
            # CREATE SUBSCRIPTION
            # =========================

            subscription = (
                self.stripe_service
                .create_subscription(
                    customer_id=dto.stripe_customer_id,
                    monthly_amount=(
                        contract.monthly_payment
                    ),
                    application_id=(
                        contract.application_id
                    ),
                )
            )

            # =========================
            # UPDATE CONTRACT
            # =========================

            contract.stripe_customer_id = (
                dto.stripe_customer_id
            )

            contract.stripe_subscription_id = (
                subscription.id
            )

            contract.subscription_status = (
                SubscriptionStatusMapper
                .from_stripe(
                    subscription.status
                )
            )

            self.financing_contract_repository.update(
                contract
            )

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                type=EventType.SUBSCRIPTION_CREATED,
                message=(
                    "Abonnement de financement créé."
                ),
                application_id=(
                    application.id
                ),
                vehicle_id=(
                    application.vehicle_id
                ),
                user_id=dto.user_id,
                event_metadata={
                    "contract_id": contract.id,
                    "stripe_customer_id": dto.stripe_customer_id,
                    "stripe_subscription_id": (
                        subscription.id
                    ),
                    "monthly_payment": (
                        contract.monthly_payment
                    ),
                },
            )

            # =========================
            # SUCCESS LOG
            # =========================

            logger.info(
                "Abonnement Stripe créé",
                extra={
                    "contract_id": contract.id,
                    "application_id": (
                        application.id
                    ),
                    "stripe_customer_id": (
                        dto.stripe_customer_id
                    ),
                    "stripe_subscription_id": (
                        subscription.id
                    ),
                    "user_id": dto.user_id,
                },
            )

            # =========================
            # RESULT
            # =========================

            return CreateSubscriptionResult(
                contract_id=contract.id,
                stripe_customer_id=(
                    dto.stripe_customer_id
                ),
                stripe_subscription_id=(
                    subscription.id
                ),
                subscription_status=(
                    contract.subscription_status.value
                ),
            )

        except Exception:

            logger.exception(
                "Erreur création abonnement Stripe",
                extra={
                    "contract_id": (
                        contract.id
                        if contract
                        else dto.contract_id
                    ),
                    "user_id": dto.user_id,
                },
            )

            raise