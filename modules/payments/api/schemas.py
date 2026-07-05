from pydantic import BaseModel, Field, EmailStr, field_validator


class CreatePaymentDTO(BaseModel):

    application_id: str = Field(..., min_length=1)

    user_id: str = Field(..., min_length=1)

    amount: float = Field(
        ...,
        gt=0,
        description="Montant du paiement en euros"
    )

    product_name: str = Field(
        ...,
        min_length=3,
        max_length=255
    )

    email: EmailStr | None = None

    # =========================
    # VALIDATIONS MÉTIER
    # =========================

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value):

        if value <= 0:
            raise ValueError("Le montant doit être supérieur à 0")

        if value > 1_000_000:
            raise ValueError("Montant trop élevé")

        return value

    # =========================
    # VALIDATION PRODUCT NAME
    # =========================
    @field_validator("product_name")
    @classmethod
    def validate_product_name(cls, value):

        if not value.strip():
            raise ValueError("Nom du produit invalide")

        return value.strip()