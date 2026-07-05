from sqlalchemy.orm import Session

from modules.financing.infrastructure.db.installment_model import (
    InstallmentPaymentModel
)

from modules.financing.domain.entities.installment import (
    InstallmentPayment
)

from modules.core.enums import InstallmentStatus

class InstallmentRepositorySQL:

    def __init__(self, session: Session):

        self.session = session

    # =========================
    # SAVE ONE
    # =========================
    def save(self, installment: InstallmentPayment):

        model = InstallmentPaymentModel(

            id=installment.id,

            financing_contract_id=installment.financing_contract_id,
            
            installment_number=installment.installment_number,

            amount=installment.amount,

            due_date=installment.due_date,

            status=installment.status,

            paid_at=installment.paid_at,

            stripe_invoice_id=installment.stripe_invoice_id
        )

        self.session.merge(model)

    # =========================
    # SAVE MANY
    # =========================
    def save_all(self, installments):

        for inst in installments:

            model = InstallmentPaymentModel(

                id=inst.id,

                financing_contract_id=inst.financing_contract_id,

                installment_number=inst.installment_number,

                amount=inst.amount,

                due_date=inst.due_date,

                status=inst.status,

                paid_at=inst.paid_at,

                stripe_invoice_id=inst.stripe_invoice_id
            )

            self.session.add(model)

    # =========================
    # GET BY ID
    # =========================
    def get_by_id(self, installment_id: str):

        model = (
            self.session.query(InstallmentPaymentModel)
            .filter_by(id=installment_id)
            .first()
        )

        if not model:
            return None

        return model

    # =========================
    # NEXT PENDING
    # =========================
    def find_next_unpaid(
            self,
            contract_id: str
        ):
            return (
                self.session.query(
                    InstallmentPaymentModel
                )
                .filter(
                    InstallmentPaymentModel.financing_contract_id
                    == contract_id,

                    InstallmentPaymentModel.status.in_([
                        InstallmentStatus.PENDING,
                        InstallmentStatus.FAILED
                    ])
                )
                .order_by(
                    InstallmentPaymentModel.due_date.asc()
                )
                .first()
            )

    # =========================
    # COUNT
    # =========================
    def count_by_contract_id(self, contract_id: str):

        return (
            self.session.query(InstallmentPaymentModel)
            .filter_by(financing_contract_id=contract_id)
            .count()
        )

    # =========================
    # COMMIT
    # =========================
    def commit(self):

        self.session.commit()