from sqlalchemy.orm import Session

from modules.payments.domain.entities.payment import Payment
from modules.payments.domain.enums import PaymentStatus
from modules.payments.domain.exceptions import PaymentNotFound
from modules.payments.domain.repositories.payment_repository import (
    PaymentRepository,
)

from modules.payments.infrastructure.db.payment_model import (
    PaymentModel,
)

from modules.payments.infrastructure.mappers.payment_mapper import (
    PaymentMapper,
)


class PaymentRepositorySQL(PaymentRepository):

    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    # =====================================================
    # SAVE
    # =====================================================

    def save(
        self,
        payment: Payment,
    ) -> Payment:

        model = (
            self.session
            .query(PaymentModel)
            .filter(
                PaymentModel.id == payment.id
            )
            .first()
        )

        if model:

            PaymentMapper.update_model(
                model,
                payment,
            )

        else:

            model = PaymentMapper.to_model(
                payment
            )

            self.session.add(
                model
            )

        self.session.flush()

        return PaymentMapper.to_domain(
            model
        )

    # =====================================================
    # GET BY ID
    # =====================================================

    def get_by_id(
        self,
        payment_id: str,
    ) -> Payment | None:

        model = (
            self.session
            .query(PaymentModel)
            .filter(
                PaymentModel.id == payment_id
            )
            .first()
        )

        if model is None:
            return None

        return PaymentMapper.to_domain(
            model
        )

    # =====================================================
    # GET BY STRIPE SESSION ID
    # =====================================================

    def get_by_session_id(
        self,
        stripe_session_id: str,
    ) -> Payment | None:

        model = (
            self.session
            .query(PaymentModel)
            .filter(
                PaymentModel.stripe_session_id
                == stripe_session_id
            )
            .first()
        )

        if model is None:
            return None

        return PaymentMapper.to_domain(
            model
        )

    # =====================================================
    # GET BY APPLICATION + STATUS
    # =====================================================

    def get_by_application_and_status(
        self,
        application_id: str,
        status: PaymentStatus,
    ) -> Payment | None:

        model = (
            self.session
            .query(PaymentModel)
            .filter(
                PaymentModel.application_id
                == application_id,

                PaymentModel.status
                == status,
            )
            .order_by(
                PaymentModel.created_at.desc()
            )
            .first()
        )

        if model is None:
            return None

        return PaymentMapper.to_domain(
            model
        )

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        payment: Payment,
    ) -> Payment:

        model = (
            self.session
            .query(PaymentModel)
            .filter(
                PaymentModel.id == payment.id
            )
            .first()
        )

        if model is None:
            raise PaymentNotFound()

        PaymentMapper.update_model(
            model,
            payment,
        )

        self.session.flush()

        return PaymentMapper.to_domain(
            model
        )

    def get_latest_payment(
        self,
        application_id: str,
    ) -> Payment | None:

        model = (
            self.session
.query(PaymentModel)
            .filter(
                PaymentModel.application_id == application_id
            )
            .order_by(
                PaymentModel.created_at.desc()
            )
            .first()
        )

        if model is None:
            return None

        return PaymentMapper.to_domain(model)