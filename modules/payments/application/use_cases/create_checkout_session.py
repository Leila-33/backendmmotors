import logging
from datetime import datetime, timezone
from uuid import uuid4
from core.config.settings import settings

from modules.auth.domain.exceptions import Forbidden
from modules.applications.domain.exceptions import (
    ApplicationNotFound,
)

from modules.applications.domain.enums import (
    ApplicationStatus,
    EventType,
)


from modules.payments.domain.entities.payment import Payment
from modules.payments.domain.enums import PaymentStatus
from modules.payments.domain.exceptions import PaymentNotAllowed
from modules.payments.application.results.create_checkout_session_result import (
    CreateCheckoutSessionResult,
)
from modules.payments.application.dtos.create_checkout_session_dto import (
    CreateCheckoutSessionDTO
)
from modules.vehicles.domain.enums import VehicleType

logger = logging.getLogger(__name__)


class CreateCheckoutSessionUseCase:

    def __init__(
        self,
        payment_repository,
        stripe_service,
        application_repository,
        event_service,
        unit_of_work,
    ):
        self.payment_repository = payment_repository
        self.stripe_service = stripe_service
        self.application_repository = application_repository
        self.event_service = event_service
        self.unit_of_work = unit_of_work

    def execute(
        self,
        dto: CreateCheckoutSessionDTO,
    ):

        try:

            # =========================
            # APPLICATION
            # =========================

            application = (
                self.application_repository
                .get_by_id(dto.application_id)
            )

            if application is None:
                raise ApplicationNotFound()

            # =========================
            # VÉRIFICATION PROPRIÉTAIRE
            # =========================

            if application.user_id != dto.user_id:
                raise Forbidden(
                    "Vous n'êtes pas autorisé à effectuer "
                    "ce paiement."
                )

            # =========================
            # STATUT
            # =========================

            if application.status != ApplicationStatus.APPROVED:
                raise PaymentNotAllowed()

            # =========================
            # MONTANT DU PAIEMENT
            # =========================

            if application.vehicle is None:
                raise PaymentNotAllowed(
                    "Le véhicule associé au dossier est introuvable."
                )

            vehicle_type = application.vehicle.type

            # -------------------------
            # LOCATION
            # -------------------------

            if vehicle_type == VehicleType.RENT:

                if application.total_price is None:
                    raise PaymentNotAllowed(
                        "Le montant de la location est introuvable."
                    )

                amount = float(
                    application.total_price
                )

            # -------------------------
            # VENTE
            # -------------------------

            elif vehicle_type == VehicleType.SALE:

                if application.financing is None:
                    raise PaymentNotAllowed(
                        "Les informations de financement sont introuvables."
                    )

                if application.financing.down_payment is None:
                    raise PaymentNotAllowed(
                        "L'apport initial est introuvable."
                    )

                amount = float(
                    application.financing.down_payment
                )

            # -------------------------
            # TYPE INCONNU
            # -------------------------

            else:

                raise PaymentNotAllowed(
                    "Le type de véhicule ne permet pas ce paiement."
                )

            # =========================
            # VALIDATION DU MONTANT
            # =========================

            if amount <= 0:
                raise PaymentNotAllowed(
                    "Le montant du paiement doit être supérieur à zéro."
                )

            # =========================
            # DÉJÀ PAYÉ
            # =========================

            payment = (
                self.payment_repository
                .get_by_application_and_status(
                    application.id,
                    PaymentStatus.PAID,
                )
            )

            if payment:

                logger.info(
                    "Paiement déjà effectué",
                    extra={
                        "application_id": application.id,
                        "payment_id": payment.id,
                    },
                )

                return CreateCheckoutSessionResult(
                    checkout_url=None,
                    payment_id=payment.id,
                )

            # =========================
            # INFORMATIONS CLIENT
            # =========================

            customer_email = application.email

            customer_name = (
                f"{application.first_name or ''} "
                f"{application.last_name or ''}"
            ).strip()

            if not customer_email:
                raise PaymentNotAllowed(
                    "L'adresse email du client est introuvable."
                )

            if not customer_name:
                raise PaymentNotAllowed(
                    "Le nom du client est introuvable."
                )

            # =========================
            # NOM DU PRODUIT
            # =========================

            product_name = (
                self._build_product_name(
                    application
                )
            )

            # =========================
            # STRIPE CUSTOMER
            # =========================

            stripe_customer_id = (
                self.stripe_service
                .get_or_create_customer(
                    email=customer_email,
                    name=customer_name,
                )
            )

            # =========================
            # STRIPE SESSION
            # =========================

            session = (
                self.stripe_service
                .create_checkout_session(
                    application_id=application.id,
                    amount=amount,
                    product_name=product_name,
                    success_url=settings.SUCCESS_URL,
                    cancel_url=settings.CANCEL_URL,
                    customer_id=stripe_customer_id,
                )
            )

            # =========================
            # PAIEMENT EXISTANT
            # =========================

            payment = (
                self.payment_repository
                .get_by_application_and_status(
                    application.id,
                    PaymentStatus.PENDING,
                )
            )

            if payment is None:

                payment = (
                    self.payment_repository
                    .get_by_application_and_status(
                        application.id,
                        PaymentStatus.FAILED,
                    )
                )

            # =========================
            # CRÉATION DU PAIEMENT
            # =========================

            if payment is None:

                payment = Payment(
                    id=str(uuid4()),
                    application_id=application.id,
                    user_id=application.user_id,

                    amount=amount,

                    currency="eur",

                    stripe_customer_id=(
                        stripe_customer_id
                    ),

                    stripe_session_id=session.id,

                    stripe_payment_intent_id=None,

                    status=PaymentStatus.PENDING,

                    description=product_name,

                    created_at=datetime.now(
                        timezone.utc
                    ),
                )

                self.payment_repository.save(
                    payment
                )

            # =========================
            # RÉUTILISATION DU PAIEMENT
            # =========================

            else:

                payment.amount = amount


                payment.stripe_customer_id = (
                    stripe_customer_id
                )

                payment.stripe_session_id = (
                    session.id
                )

                payment.stripe_payment_intent_id = (
                    None
                )

                payment.description = (
                    product_name
                )

                payment.status = (
                    PaymentStatus.PENDING
                )

                self.payment_repository.update(
                    payment
                )

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                type=EventType.PAYMENT_INITIATED,

                message="Paiement initialisé",

                user_id=application.user_id,

                application_id=application.id,

                vehicle_id=application.vehicle_id,

                event_metadata={
                    "payment_id": payment.id,
                    "amount": payment.amount,
                    "stripe_session_id": session.id,
                    "stripe_customer_id": (
                        stripe_customer_id
                    ),
                },
            )

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

            # =========================
            # LOG
            # =========================

            logger.info(
                "Session checkout Stripe créée",
                extra={
                    "application_id": application.id,
                    "payment_id": payment.id,
                    "stripe_session_id": session.id,
                    "stripe_customer_id": (
                        stripe_customer_id
                    ),
                },
            )

            # =========================
            # RESULTAT
            # =========================

            return CreateCheckoutSessionResult(
                checkout_url=session.url,
                payment_id=payment.id,
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur création session checkout Stripe",
                extra={
                    "application_id": dto.application_id,
                    "user_id": dto.user_id,
                },
            )

            raise

    def _build_product_name(
        self,
        application,
    ) -> str:

        if application.vehicle:

            brand = (
                application.vehicle.brand or ""
            )

            model = (
                application.vehicle.model or ""
            )

            name = (
                f"{brand} {model}"
            ).strip()

            if name:
                return name

        return "Paiement M-Motors"