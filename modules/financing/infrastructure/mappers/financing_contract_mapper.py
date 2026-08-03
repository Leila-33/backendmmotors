from modules.financing.domain.entities.financing_contract import (
    FinancingContract
)

from modules.financing.infrastructure.db.financing_contract_model import (
    FinancingContractModel
)


class FinancingContractMapper:


    # =====================================================
    # ORM -> DOMAIN
    # =====================================================

    @staticmethod
    def to_domain(
        model: FinancingContractModel
    ) -> FinancingContract:

        return FinancingContract(

            id=model.id,

            application_id=model.application_id,

            financed_amount=model.financed_amount,

            monthly_payment=model.monthly_payment,

            duration_months=model.duration_months,

            remaining_balance=model.remaining_balance,

            stripe_customer_id=model.stripe_customer_id,

            stripe_subscription_id=model.stripe_subscription_id,

            subscription_status=model.subscription_status,

            created_at=model.created_at,

            updated_at=model.updated_at,

        )


    # =====================================================
    # DOMAIN -> ORM
    # =====================================================

    @staticmethod
    def to_model(
        entity: FinancingContract
    ) -> FinancingContractModel:

        return FinancingContractModel(

            id=entity.id,

            application_id=entity.application_id,

            financed_amount=entity.financed_amount,

            monthly_payment=entity.monthly_payment,

            duration_months=entity.duration_months,

            remaining_balance=entity.remaining_balance,

            stripe_customer_id=entity.stripe_customer_id,

            stripe_subscription_id=entity.stripe_subscription_id,

            subscription_status=entity.subscription_status,

            created_at=entity.created_at,

            updated_at=entity.updated_at,

        )


    # =====================================================
    # UPDATE EXISTING ORM MODEL
    # =====================================================

    @staticmethod
    def update_model(
        model: FinancingContractModel,
        entity: FinancingContract
    ) -> FinancingContractModel:


        model.financed_amount = (
            entity.financed_amount
        )

        model.monthly_payment = (
            entity.monthly_payment
        )

        model.duration_months = (
            entity.duration_months
        )

        model.remaining_balance = (
            entity.remaining_balance
        )


        model.stripe_customer_id = (
            entity.stripe_customer_id
        )

        model.stripe_subscription_id = (
            entity.stripe_subscription_id
        )


        model.subscription_status = (
            entity.subscription_status
        )


        model.updated_at = (
            entity.updated_at
        )


        return model