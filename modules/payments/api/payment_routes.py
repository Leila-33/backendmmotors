from fastapi import APIRouter, Depends, Request
from modules.payments.application.use_cases.create_checkout_session import CreateCheckoutSessionUseCase
from modules.payments.api.schemas import (
    CreateCheckoutSessionDTO,
    CreateCheckoutSessionResponse
)

from modules.payments.api.dependencies import (
    get_create_checkout_session_usecase,
    get_handle_payment_success_usecase,
    get_stripe_service,
    get_handle_subscription_payment_usecase,
    get_handle_invoice_created_usecase
)

router = APIRouter(tags=["Payments"])

# =========================================================
# CREATE CHECKOUT SESSION
# =========================================================
@router.post(
    "/checkout",
    response_model=CreateCheckoutSessionResponse,
)
def create_checkout_session(
    dto: CreateCheckoutSessionDTO,
    use_case: CreateCheckoutSessionUseCase = Depends(
        get_create_checkout_session_usecase
    ),
):

    return use_case.execute(dto)


# =========================================================
# STRIPE WEBHOOK
# =========================================================
@router.post("/webhook")
async def stripe_webhook(

    request: Request,

    stripe_service=Depends(
        get_stripe_service
    ),

    payment_success_uc=Depends(
        get_handle_payment_success_usecase
    ),

    invoice_created_uc=Depends(
        get_handle_invoice_created_usecase
    ),

    subscription_payment_uc=Depends(
        get_handle_subscription_payment_usecase
    )
):

    payload = await request.body()

    sig_header = request.headers.get(
        "stripe-signature"
    )


    event = stripe_service.verify_webhook(
        payload,
        sig_header
    )


    event_type = event["type"]



    # =====================================
    # ACOMPTE
    # =====================================

    if event_type == "checkout.session.completed":

        session = event["data"]["object"]

        payment_success_uc.execute(
            stripe_session_id=session["id"]
        )



    # =====================================
    # CREATION FACTURE MENSUALITE
    # =====================================

    elif event_type == "invoice.created":

        invoice_created_uc.execute(
            event
        )



    # =====================================
    # PAIEMENT MENSUALITE
    # =====================================

    elif event_type in [
        "invoice.paid",
        "invoice.payment_failed"
    ]:

        subscription_payment_uc.execute(
            event
        )


    return {
        "received": True
    }