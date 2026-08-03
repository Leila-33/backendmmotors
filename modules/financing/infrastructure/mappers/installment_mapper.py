from modules.financing.domain.entities.installment import (
    InstallmentPayment
)

from modules.financing.infrastructure.db.installment_model import (
    InstallmentPaymentModel
)


class InstallmentPaymentMapper:


    # =====================================================
    # ORM -> DOMAIN
    # =====================================================

    @staticmethod
    def to_domain(
        model: InstallmentPaymentModel
    ) -> InstallmentPayment:

        return InstallmentPayment(

            id=model.id,

            financing_contract_id=(
                model.financing_contract_id
            ),

            installment_number=(
                model.installment_number
            ),

            amount=model.amount,

            due_date=model.due_date,

            paid_at=model.paid_at,

            status=model.status,

            stripe_invoice_id=(
                model.stripe_invoice_id
            ),

            created_at=model.created_at,
        )


    # =====================================================
    # DOMAIN -> ORM
    # =====================================================

    @staticmethod
    def to_model(
        entity: InstallmentPayment
    ) -> InstallmentPaymentModel:

        return InstallmentPaymentModel(

            id=entity.id,

            financing_contract_id=(
                entity.financing_contract_id
            ),

            installment_number=(
                entity.installment_number
            ),

            amount=entity.amount,

            due_date=entity.due_date,

            paid_at=entity.paid_at,

            status=entity.status,

            stripe_invoice_id=(
                entity.stripe_invoice_id
            ),

            created_at=entity.created_at,

        )


    # =====================================================
    # UPDATE EXISTING MODEL
    # =====================================================

    @staticmethod
    def update_model(
        model: InstallmentPaymentModel,
        entity: InstallmentPayment
    ) -> InstallmentPaymentModel:


        model.amount = entity.amount

        model.due_date = entity.due_date

        model.paid_at = entity.paid_at

        model.status = entity.status

        model.stripe_invoice_id = (
            entity.stripe_invoice_id
        )


        return model