from pydantic import BaseModel, Field, EmailStr, field_validator

# =========================================================
# CREATE CHECKOUT SESSION
# =========================================================
class CreateCheckoutSessionRequest(BaseModel):

    application_id: str = Field(..., min_length=1)



class CreateCheckoutSessionResponse(BaseModel):

    checkout_url: str | None

    payment_id: str


# =========================================================
# STRIPE WEBHOOK
# =========================================================

class StripeWebhookResponse(BaseModel):

    received: bool