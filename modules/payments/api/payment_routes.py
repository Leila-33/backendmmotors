from fastapi import (
    APIRouter,
    Depends,
    Request,
)

# =========================================================
# SECURITY
# =========================================================

from core.security.dependencies import (
    get_current_user,
)
from modules.auth.domain.entities.user import User

# =========================================================
# USE CASES
# =========================================================

from modules.payments.application.use_cases.create_checkout_session import (
    CreateCheckoutSessionUseCase,
)

from modules.payments.application.use_cases.handle_payment_success import (
    HandlePaymentSuccessUseCase,
)

from modules.payments.application.use_cases.handle_invoice_created import (
    HandleInvoiceCreatedUseCase,
)

from modules.payments.application.use_cases.handle_subscription_payment import (
    HandleSubscriptionPaymentUseCase,
)

# =========================================================
# DTOs
# =========================================================

from modules.payments.application.dtos.create_checkout_session_dto import (
    CreateCheckoutSessionDTO,
)

from modules.payments.application.dtos.handle_payment_success_dto import (
    HandlePaymentSuccessDTO,
)

from modules.payments.application.dtos.handle_invoice_created_dto import (
    HandleInvoiceCreatedDTO,
)

from modules.payments.application.dtos.handle_subscription_payment_dto import (
    HandleSubscriptionPaymentDTO,
)

# =========================================================
# API SCHEMAS
# =========================================================

from modules.payments.api.schemas import (
    CreateCheckoutSessionRequest,
    CreateCheckoutSessionResponse,
    StripeWebhookResponse,
)

# =========================================================
# DEPENDENCIES
# =========================================================

from modules.payments.api.dependencies import (
    get_create_checkout_session_usecase,
    get_handle_payment_success_usecase,
    get_handle_invoice_created_usecase,
    get_handle_subscription_payment_usecase,
    get_stripe_service,
)

# =========================================================
# MAPPER
# =========================================================

from modules.payments.infrastructure.mappers.payment_mapper import (
    PaymentMapper,
)


router = APIRouter(
    tags=["Payments"]
)


# =========================================================
# CREATE CHECKOUT SESSION
# =========================================================

@router.post(
    "/checkout",
    response_model=CreateCheckoutSessionResponse,
)
def create_checkout_session(

    request: CreateCheckoutSessionRequest,

    current_user: User = Depends(
        get_current_user
    ),

    usecase: CreateCheckoutSessionUseCase = Depends(
        get_create_checkout_session_usecase
    ),
):

    # =====================================================
    # DTO
    # =====================================================

    dto = CreateCheckoutSessionDTO(
        application_id=request.application_id,
        user_id=current_user.id,
        amount=request.amount,
        product_name=request.product_name,
        email=request.email,
    )

    # =====================================================
    # USE CASE
    # =====================================================

    result = usecase.execute(
        dto
    )

    # =====================================================
    # RESPONSE
    # =====================================================

    return PaymentMapper.to_checkout_session_response(
        result
    )


# =========================================================
# STRIPE WEBHOOK
# =========================================================

@router.post(
    "/webhook",
    response_model=StripeWebhookResponse,
)
async def stripe_webhook(

    request: Request,

    stripe_service=Depends(
        get_stripe_service
    ),

    payment_success_uc: HandlePaymentSuccessUseCase = Depends(
        get_handle_payment_success_usecase
    ),

    invoice_created_uc: HandleInvoiceCreatedUseCase = Depends(
        get_handle_invoice_created_usecase
    ),

    subscription_payment_uc: HandleSubscriptionPaymentUseCase = Depends(
        get_handle_subscription_payment_usecase
    ),
):

    # =====================================================
    # READ PAYLOAD
    # =====================================================

    payload = await request.body()

    sig_header = request.headers.get(
        "stripe-signature"
    )

    # =====================================================
    # VERIFY STRIPE SIGNATURE
    # =====================================================

    event = stripe_service.verify_webhook(
        payload,
        sig_header,
    )

    event_type = event["type"]


    # =====================================================
    # ACOMPTE
    # checkout.session.completed
    # =====================================================

    if event_type == "checkout.session.completed":

        session = event["data"]["object"]

        dto = HandlePaymentSuccessDTO(
            stripe_session_id=session["id"],
        )

        payment_success_uc.execute(
            dto
        )


    # =====================================================
    # CRÉATION DE FACTURE
    # invoice.created
    # =====================================================

    elif event_type == "invoice.created":

        invoice = event["data"]["object"]

        subscription_id = invoice.get(
            "subscription"
        )

        # Une facture sans abonnement
        # ne concerne pas le financement.

        if subscription_id:

            dto = HandleInvoiceCreatedDTO(
                invoice_id=invoice["id"],
                subscription_id=subscription_id,
            )

            invoice_created_uc.execute(
                dto
            )


    # =====================================================
    # PAIEMENT MENSUALITÉ
    # invoice.paid
    # invoice.payment_failed
    # =====================================================

    elif event_type in (
        "invoice.paid",
        "invoice.payment_failed",
    ):

        invoice = event["data"]["object"]

        dto = HandleSubscriptionPaymentDTO(
            event_type=event_type,
            invoice_id=invoice["id"],
        )

        subscription_payment_uc.execute(
            dto
        )


    # =====================================================
    # STRIPE ACKNOWLEDGEMENT
    # =====================================================

    return StripeWebhookResponse(
        received=True
    )