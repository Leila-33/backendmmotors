import os
import stripe



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
        customer_email: str | None = None
    ):
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

        session = stripe.checkout.Session.create(

            payment_method_types=["card"],

            mode="payment",

            customer_email=customer_email,

            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": product_name
                    },
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1
            }],

            success_url=success_url,
            cancel_url=cancel_url,

            metadata={
                "application_id": application_id
            }
        )

        return session

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
    



    def create_customer(
        self,
        email: str,
        name: str
    ):
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

        customer = stripe.Customer.create(
            email=email,
            name=name
        )

        return customer

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