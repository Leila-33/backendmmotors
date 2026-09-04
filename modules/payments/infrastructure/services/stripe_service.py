import os
import stripe
import logging

logger = logging.getLogger(__name__)

class StripeService:

    # =========================
    # CREATE CHECKOUT SESSION
    # =========================
    def create_checkout_session(
        self,
        application_id: str,
        amount: float,
        product_name: str,
        success_url: str,
        cancel_url: str,
        customer_id: str,
    ):
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],

            mode="payment",

            customer=customer_id,

            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {
                            "name": product_name,
                        },
                        "unit_amount": int(amount * 100),
                    },
                    "quantity": 1,
                }
            ],

            payment_intent_data={
                "setup_future_usage": "off_session",
            },

            success_url=success_url,
            cancel_url=cancel_url,

            metadata={
                "application_id": application_id,
            },
        )

        return session
    
    def set_customer_default_payment_method(
        self,
        customer_id: str,
        payment_intent_id: str,
    ):
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

        payment_intent = stripe.PaymentIntent.retrieve(
            payment_intent_id
        )

        payment_method_id = payment_intent.payment_method

        if not payment_method_id:
            raise ValueError(
                "Aucun PaymentMethod associé au PaymentIntent."
            )

        stripe.Customer.modify(
            customer_id,
            invoice_settings={
                "default_payment_method": payment_method_id
            },
        )

        return payment_method_id
    
    # =========================
    # VERIFY WEBHOOK (IMPORTANT)
    # =========================
    def verify_webhook(
        self,
        payload: bytes,
        sig_header: str
    ):

        webhook_secret = os.getenv(
            "STRIPE_WEBHOOK_SECRET"
        )

        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=webhook_secret
        )

        return event

    def get_or_create_customer(
        self,
        email: str,
        name: str,
    ):
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

        # =========================
        # SEARCH EXISTING CUSTOMER
        # =========================

        customers = stripe.Customer.list(
            email=email,
            limit=1,
        )

        if customers.data:

            customer = customers.data[0]

            logger.info(
                "Customer Stripe existant réutilisé",
                extra={
                    "stripe_customer_id": customer.id,
                    "email": email,
                },
            )

            return customer.id

        # =========================
        # CREATE CUSTOMER
        # =========================

        customer = stripe.Customer.create(
            email=email,
            name=name,
        )

        logger.info(
            "Customer Stripe créé",
            extra={
                "stripe_customer_id": customer.id,
                "email": email,
            },
        )

        return customer.id

    def create_subscription(
        self,
        customer_id: str,
        monthly_amount: float,
        application_id: str
    ):
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

        # Stripe nécessite un "price" pour subscription
        # donc on crée un price dynamique (simple version)
        price = stripe.Price.create(
            unit_amount=int(monthly_amount * 100),
            currency="eur",
            recurring={"interval": "month"},
            product_data={
                "name": "Financing subscription"
            }
        )

        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{
                "price": price.id
            }],
            metadata={
                "application_id": application_id
            },
            expand=["latest_invoice.payment_intent"]
        )

        return subscription