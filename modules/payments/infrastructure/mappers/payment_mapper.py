from modules.payments.infrastructure.db.payment_model import PaymentModel

from modules.payments.domain.entities.payment import Payment


# =========================
# MODEL → DOMAIN
# =========================
def to_domain(model: PaymentModel) -> Payment:

    return Payment(

        id=model.id,

        # relations
        application_id=model.application_id,
        user_id=model.user_id,

        # stripe
        stripe_session_id=model.stripe_session_id,
        stripe_payment_intent_id=model.stripe_payment_intent_id,

        # financial
        amount=model.amount,
        currency=model.currency,

        # status
        status=model.status,

        # metadata
        description=model.description,

        # timestamps
        created_at=model.created_at,
        updated_at=model.updated_at
    )


# =========================
# DOMAIN → MODEL
# =========================
def to_model(domain: Payment) -> PaymentModel:

    return PaymentModel(

        id=domain.id,

        # relations
        application_id=domain.application_id,
        user_id=domain.user_id,

        # stripe
        stripe_session_id=domain.stripe_session_id,
        stripe_payment_intent_id=domain.stripe_payment_intent_id,

        # financial
        amount=domain.amount,
        currency=domain.currency,

        # status
        status=domain.status,

        # metadata
        description=domain.description,

        # timestamps
        created_at=domain.created_at,
        updated_at=domain.updated_at
    )