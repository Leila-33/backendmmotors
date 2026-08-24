from modules.payments.infrastructure.db.payment_model import PaymentModel

from modules.payments.domain.entities.payment import Payment
from modules.payments.api.schemas import CreateCheckoutSessionResponse
from modules.payments.application.results.create_checkout_session_result import CreateCheckoutSessionResult

class PaymentMapper:

    @staticmethod
    def to_domain(model: PaymentModel) -> Payment:

        return Payment(
            id=model.id,

            application_id=model.application_id,
            user_id=model.user_id,

            stripe_session_id=model.stripe_session_id,
            stripe_payment_intent_id=model.stripe_payment_intent_id,

            amount=model.amount,
            currency=model.currency,

            status=model.status,

            description=model.description,

            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Payment) -> PaymentModel:

        return PaymentModel(
            id=entity.id,

            application_id=entity.application_id,
            user_id=entity.user_id,

            stripe_session_id=entity.stripe_session_id,
            stripe_payment_intent_id=entity.stripe_payment_intent_id,

            amount=entity.amount,
            currency=entity.currency,

            status=entity.status,

            description=entity.description,

            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def update_model(
        model: PaymentModel,
        entity: Payment,
    ) -> PaymentModel:

        model.application_id = entity.application_id
        model.user_id = entity.user_id

        model.stripe_session_id = entity.stripe_session_id
        model.stripe_payment_intent_id = entity.stripe_payment_intent_id

        model.amount = entity.amount
        model.currency = entity.currency

        model.status = entity.status

        model.description = entity.description

        model.created_at = entity.created_at
        model.updated_at = entity.updated_at

        return model


    @staticmethod
    def to_checkout_session_response(
    result: CreateCheckoutSessionResult,
) -> CreateCheckoutSessionResponse:

        return CreateCheckoutSessionResponse(
            checkout_url=result.checkout_url,
            payment_id=result.payment_id,
        )
