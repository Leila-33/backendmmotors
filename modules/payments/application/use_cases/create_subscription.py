from modules.core.enums import SubscriptionStatus

from uuid import uuid4


from modules.core.exceptions import (
    FinancingContractNotFound
)
from modules.core.enums import EventType
from modules.applications.domain.entities.event import Event

STRIPE_TO_SUBSCRIPTION_STATUS = {
    "active": SubscriptionStatus.ACTIVE,
    "past_due": SubscriptionStatus.PAST_DUE,
    "canceled": SubscriptionStatus.CANCELLED,
    "incomplete": SubscriptionStatus.PAST_DUE,
    "incomplete_expired": SubscriptionStatus.CANCELLED,
    "trialing": SubscriptionStatus.ACTIVE,
}

class CreateSubscriptionUseCase:

    def __init__(
        self,
        stripe_service,
        financing_contract_repository,
        event_repository
    ):

        self.stripe_service = stripe_service

        self.financing_contract_repository = (
            financing_contract_repository
        )

        self.event_repository = (
            event_repository
        )

    # =========================
    # EXECUTE
    # =========================
    def execute(
        self,
        contract,
        customer_email: str,
        customer_name: str,
        user_id: str
    ):

        if not contract:
            raise FinancingContractNotFound()

        # =========================
        # IDEMPOTENCE
        # =========================
        if contract.stripe_subscription_id:
            return contract

        # =========================
        # CREATE CUSTOMER
        # =========================
        customer = (
            self.stripe_service.create_customer(
                email=customer_email,
                name=customer_name
            )
        )

        # =========================
        # CREATE SUBSCRIPTION
        # =========================
        subscription = (
            self.stripe_service.create_subscription(
                customer_id=customer.id,
                monthly_amount=contract.monthly_payment,
                application_id=contract.application_id
            )
        )

        # =========================
        # SAVE STRIPE IDS
        # =========================
        contract.stripe_customer_id = (
            customer.id
        )

        contract.stripe_subscription_id = (
            subscription.id
        )

        contract.subscription_status = (
            STRIPE_TO_SUBSCRIPTION_STATUS.get(
                subscription.status,
                SubscriptionStatus.ACTIVE
            )
        )

        self.financing_contract_repository.update(
            contract
        )

        # =========================
        # EVENT
        # =========================
        self.event_repository.save(
            Event(
                id=str(uuid4()),
                application_id=contract.application_id,
                user_id=user_id,
                type=EventType.SUBSCRIPTION_CREATED,
                message=(
                    "Abonnement de financement créé."
                ),
                event_metadata={
                    "contract_id": contract.id,
                    "stripe_customer_id": customer.id,
                    "stripe_subscription_id": subscription.id,
                    "monthly_payment": contract.monthly_payment
                }
            )
        )

        self.event_repository.commit()

        return contract

    