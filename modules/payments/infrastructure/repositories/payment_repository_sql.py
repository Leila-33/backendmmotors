from modules.payments.domain.repositories.payment_repository import (
    PaymentRepository
)

from modules.payments.infrastructure.db.payment_model import PaymentModel

from modules.payments.infrastructure.mappers.payment_mapper import (
    to_domain,
    to_model
)


class PaymentRepositorySQL(PaymentRepository):

    def __init__(self, session):
        self.session = session

    # =========================
    # SAVE
    # =========================
    def save(self, payment):

        model = to_model(payment)

        self.session.add(model)

    # =========================
    # UPDATE
    # =========================
    def update(self, payment):

        model = to_model(payment)

        self.session.merge(model)

    # =========================
    # GET BY ID
    # =========================
    def get_by_id(self, payment_id: str):

        model = (
            self.session.query(PaymentModel)
            .filter(PaymentModel.id == payment_id)
            .first()
        )

        if not model:
            return None

        return to_domain(model)

    # =========================
    # GET BY STRIPE SESSION ID
    # =========================
    def get_by_session_id(
        self,
        stripe_session_id: str
    ):

        model = (
            self.session.query(PaymentModel)
            .filter(
                PaymentModel.stripe_session_id
                == stripe_session_id
            )
            .first()
        )

        if not model:
            return None

        return to_domain(model)

    # =========================
    # COMMIT
    # =========================
    def commit(self):

        self.session.commit()

    def get_by_application_id(self, application_id: str):
        return (
            self.session.query(PaymentModel)
            .filter(PaymentModel.application_id == application_id)
            .order_by(PaymentModel.created_at.desc())
            .first()
        )
    
    def get_latest_payment(self, application_id):
        return (
            self.session.query(PaymentModel)
            .filter_by(application_id=application_id)
            .order_by(PaymentModel.created_at.desc())
            .first()
        )