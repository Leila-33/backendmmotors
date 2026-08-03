from sqlalchemy.orm import Session

from modules.financing.infrastructure.db.installment_model import (
    InstallmentPaymentModel
)

from modules.financing.domain.entities.installment import (
    InstallmentPayment
)

from modules.payments.domain.enums import InstallmentStatus

from sqlalchemy.orm import Session



from modules.financing.infrastructure.mappers.installment_mapper import (
    InstallmentPaymentMapper
)

from modules.financing.domain.enums import InstallmentStatus

from modules.financing.domain.exceptions import (
    InstallmentNotFound
)


class InstallmentRepositorySQL:


    def __init__(
        self,
        session: Session
    ):

        self.session = session


    # =====================================================
    # SAVE ONE
    # =====================================================

    def save(
        self,
        installment: InstallmentPayment
    ) -> InstallmentPayment:


        model = (
            InstallmentPaymentMapper
            .to_model(installment)
        )

        self.session.add(model)

        self.session.flush()


        return (
            InstallmentPaymentMapper
            .to_domain(model)
        )


    # =====================================================
    # SAVE MANY
    # =====================================================

    def save_all(
        self,
        installments: list[InstallmentPayment]
    ):

        models = [

            InstallmentPaymentMapper
            .to_model(inst)

            for inst in installments

        ]


        self.session.add_all(models)

        self.session.flush()


        return [

            InstallmentPaymentMapper
            .to_domain(model)

            for model in models

        ]


    # =====================================================
    # FIND BY ID
    # =====================================================

    def find_by_id(
        self,
        installment_id: str
    ):

        model = (
            self.session.query(
                InstallmentPaymentModel
            )
            .filter(
                InstallmentPaymentModel.id
                == installment_id
            )
            .first()
        )


        if not model:
            return None


        return (
            InstallmentPaymentMapper
            .to_domain(model)
        )


    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        installment: InstallmentPayment
    ):


        model = (
            self.session.query(
                InstallmentPaymentModel
            )
            .filter(
                InstallmentPaymentModel.id
                == installment.id
            )
            .first()
        )


        if not model:
            raise InstallmentNotFound()


        InstallmentPaymentMapper.update_model(
            model,
            installment
        )


        self.session.flush()


        return (
            InstallmentPaymentMapper
            .to_domain(model)
        )


    # =====================================================
    # NEXT UNPAID
    # =====================================================

    def find_next_unpaid(
        self,
        contract_id: str
    ):


        model = (
            self.session.query(
                InstallmentPaymentModel
            )
            .filter(
                InstallmentPaymentModel.financing_contract_id
                == contract_id,

                InstallmentPaymentModel.status.in_(
                    [
                        InstallmentStatus.PENDING,
                        InstallmentStatus.FAILED
                    ]
                )
            )
            .order_by(
                InstallmentPaymentModel.due_date.asc()
            )
            .first()
        )


        if not model:
            return None


        return (
            InstallmentPaymentMapper
            .to_domain(model)
        )


    # =====================================================
    # COUNT
    # =====================================================

    def count_by_contract_id(
        self,
        contract_id: str
    ):

        return (
            self.session.query(
                InstallmentPaymentModel
            )
            .filter(
                InstallmentPaymentModel.financing_contract_id
                == contract_id
            )
            .count()
        )


    # =====================================================
    # GET ALL BY CONTRACT
    # =====================================================

    def find_all_by_contract_id(
        self,
        contract_id: str
    ):

        models = (
            self.session.query(
                InstallmentPaymentModel
            )
            .filter(
                InstallmentPaymentModel.financing_contract_id
                == contract_id
            )
            .order_by(
                InstallmentPaymentModel.installment_number.asc()
            )
            .all()
        )


        return [
            InstallmentPaymentMapper.to_domain(model)
            for model in models
        ]

    # =====================================================
    # FIND BY STRIPE INVOICE ID
    # =====================================================
    def find_by_stripe_invoice_id(
        self,
        stripe_invoice_id: str
    ) -> InstallmentPayment | None:

        model = (
            self.session.query(
                InstallmentPaymentModel
            )
            .filter(
                InstallmentPaymentModel.stripe_invoice_id
                == stripe_invoice_id
            )
            .first()
        )

        if not model:
            return None

        return (
            InstallmentPaymentMapper
            .to_domain(model)
        )
