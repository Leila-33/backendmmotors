from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from modules.applications.domain.enums import (
    ApplicationStatus,
    EventType,
)
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.auth.domain.exceptions import Forbidden
from modules.payments.application.dtos.create_checkout_session_dto import (
    CreateCheckoutSessionDTO,
)
from modules.payments.application.results.create_checkout_session_result import (
    CreateCheckoutSessionResult,
)
from modules.payments.application.use_cases.create_checkout_session import (
    CreateCheckoutSessionUseCase,
)
from modules.payments.domain.enums import PaymentStatus
from modules.payments.domain.exceptions import PaymentNotAllowed
from modules.vehicles.domain.enums import VehicleType


# ============================================================
# HELPERS
# ============================================================


def make_vehicle(
    *,
    vehicle_type=VehicleType.RENT,
    brand="BMW",
    model="Serie 3",
):
    return SimpleNamespace(
        id="vehicle-1",
        type=vehicle_type,
        brand=brand,
        model=model,
    )


def make_financing(
    *,
    down_payment=5000,
):
    return SimpleNamespace(
        down_payment=down_payment,
    )


_UNSET = object()


def make_application(
    *,
    application_id="application-1",
    user_id="user-1",
    status=ApplicationStatus.APPROVED,
    vehicle_type=VehicleType.RENT,
    total_price=1200,
    financing=None,
    email="leila@example.com",
    first_name="leila",
    last_name="el",
    vehicle=_UNSET,
):
    if vehicle is _UNSET:
        vehicle = make_vehicle(
            vehicle_type=vehicle_type,
        )

    return SimpleNamespace(
        id=application_id,
        user_id=user_id,
        vehicle_id="vehicle-1",
        status=status,
        vehicle=vehicle,
        total_price=total_price,
        financing=financing,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )


def make_dto(
    *,
    application_id="application-1",
    user_id="user-1",
):
    return CreateCheckoutSessionDTO(
        application_id=application_id,
        user_id=user_id,
    )


def make_session(
    *,
    session_id="session-1",
    url="https://checkout.stripe.com/session-1",
):
    return SimpleNamespace(
        id=session_id,
        url=url,
    )


def make_payment(
    *,
    payment_id="payment-1",
    status=PaymentStatus.PAID,
    amount=1200,
):
    return SimpleNamespace(
        id=payment_id,
        application_id="application-1",
        user_id="user-1",
        amount=amount,
        currency="eur",
        stripe_customer_id="cus-1",
        stripe_session_id="session-1",
        stripe_payment_intent_id=None,
        status=status,
        description="BMW Serie 3",
        created_at=datetime.now(),
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def payment_repo():
    return Mock()


@pytest.fixture
def stripe_service():
    service = Mock()

    service.get_or_create_customer.return_value = "cus-1"

    service.create_checkout_session.return_value = make_session()

    return service


@pytest.fixture
def application_repo():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    payment_repo,
    stripe_service,
    application_repo,
    event_service,
    unit_of_work,
):
    return CreateCheckoutSessionUseCase(
        payment_repository=payment_repo,
        stripe_service=stripe_service,
        application_repository=application_repo,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


# ============================================================
# APPLICATION
# ============================================================


def test_application_not_found(
    use_case,
    application_repo,
    unit_of_work,
):
    application_repo.get_by_id.return_value = None

    dto = make_dto()

    with pytest.raises(ApplicationNotFound):
        use_case.execute(dto)

    application_repo.get_by_id.assert_called_once_with(
        "application-1"
    )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_user_cannot_pay_another_users_application(
    use_case,
    application_repo,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application(
        user_id="owner-1",
    )

    dto = make_dto(
        user_id="another-user",
    )

    with pytest.raises(Forbidden):
        use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# APPLICATION STATUS
# ============================================================


@pytest.mark.parametrize(
    "status",
    [
        ApplicationStatus.DRAFT,
        ApplicationStatus.SUBMITTED,
        ApplicationStatus.REJECTED,
        ApplicationStatus.PROCESSING,
    ],
)
def test_payment_is_allowed_only_for_approved_application(
    status,
    use_case,
    application_repo,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application(
        status=status,
    )

    dto = make_dto()

    with pytest.raises(PaymentNotAllowed):
        use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# VEHICLE
# ============================================================


def test_payment_is_rejected_when_vehicle_is_missing(
    use_case,
    application_repo,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application(
        vehicle=None,
    )

    dto = make_dto()

    with pytest.raises(
        PaymentNotAllowed,
        match="véhicule associé",
    ):
        use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()


# ============================================================
# RENTAL
# ============================================================


def test_rental_payment_uses_application_total_price(
    use_case,
    application_repo,
    payment_repo,
    stripe_service,
    event_service,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application(
        vehicle_type=VehicleType.RENT,
        total_price=1500,
    )

    payment_repo.get_by_application_and_status.return_value = None

    dto = make_dto()

    with patch(
        "modules.payments.application.use_cases.create_checkout_session.settings"
    ) as settings:
        settings.SUCCESS_URL = "http://success"
        settings.CANCEL_URL = "http://cancel"

        result = use_case.execute(dto)

    assert isinstance(
        result,
        CreateCheckoutSessionResult,
    )

    stripe_service.create_checkout_session.assert_called_once()

    call_args = (
        stripe_service.create_checkout_session.call_args.kwargs
    )

    assert call_args["amount"] == 1500
    assert call_args["product_name"] == "BMW Serie 3"

    unit_of_work.commit.assert_called_once()


def test_rental_payment_is_rejected_when_total_price_is_none(
    use_case,
    application_repo,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application(
        vehicle_type=VehicleType.RENT,
        total_price=None,
    )

    dto = make_dto()

    with pytest.raises(
        PaymentNotAllowed,
        match="montant de la location",
    ):
        use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()


# ============================================================
# SALE
# ============================================================


def test_sale_payment_uses_financing_down_payment(
    use_case,
    application_repo,
    payment_repo,
    stripe_service,
    unit_of_work,
):
    financing = make_financing(
        down_payment=5000,
    )

    application_repo.get_by_id.return_value = make_application(
        vehicle_type=VehicleType.SALE,
        financing=financing,
    )

    payment_repo.get_by_application_and_status.return_value = None

    dto = make_dto()

    with patch(
        "modules.payments.application.use_cases.create_checkout_session.settings"
    ) as settings:
        settings.SUCCESS_URL = "http://success"
        settings.CANCEL_URL = "http://cancel"

        result = use_case.execute(dto)

    assert isinstance(
        result,
        CreateCheckoutSessionResult,
    )

    call_args = (
        stripe_service.create_checkout_session.call_args.kwargs
    )

    assert call_args["amount"] == 5000

    unit_of_work.commit.assert_called_once()


def test_sale_payment_is_rejected_without_financing(
    use_case,
    application_repo,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application(
        vehicle_type=VehicleType.SALE,
        financing=None,
    )

    dto = make_dto()

    with pytest.raises(
        PaymentNotAllowed,
        match="financement",
    ):
        use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()


def test_sale_payment_is_rejected_without_down_payment(
    use_case,
    application_repo,
    unit_of_work,
):
    financing = make_financing(
        down_payment=None,
    )

    application_repo.get_by_id.return_value = make_application(
        vehicle_type=VehicleType.SALE,
        financing=financing,
    )

    dto = make_dto()

    with pytest.raises(
        PaymentNotAllowed,
        match="apport initial",
    ):
        use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()


# ============================================================
# UNKNOWN VEHICLE TYPE
# ============================================================


def test_unknown_vehicle_type_is_rejected(
    use_case,
    application_repo,
    unit_of_work,
):
    vehicle = make_vehicle()

    vehicle.type = "UNKNOWN"

    application_repo.get_by_id.return_value = make_application(
        vehicle=vehicle,
    )

    dto = make_dto()

    with pytest.raises(
        PaymentNotAllowed,
        match="type de véhicule",
    ):
        use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()


# ============================================================
# AMOUNT VALIDATION
# ============================================================


@pytest.mark.parametrize(
    "amount",
    [
        0,
        -1,
        -100,
    ],
)
def test_payment_amount_must_be_positive(
    amount,
    use_case,
    application_repo,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application(
        vehicle_type=VehicleType.RENT,
        total_price=amount,
    )

    dto = make_dto()

    with pytest.raises(
        PaymentNotAllowed,
        match="supérieur à zéro",
    ):
        use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()


# ============================================================
# ALREADY PAID
# ============================================================


def test_existing_paid_payment_is_reused(
    use_case,
    application_repo,
    payment_repo,
    stripe_service,
    event_service,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application()

    paid_payment = make_payment(
        payment_id="paid-payment-1",
        status=PaymentStatus.PAID,
    )

    payment_repo.get_by_application_and_status.return_value = (
        paid_payment
    )

    dto = make_dto()

    result = use_case.execute(dto)

    assert isinstance(
        result,
        CreateCheckoutSessionResult,
    )

    assert result.checkout_url is None
    assert result.payment_id == "paid-payment-1"

    stripe_service.get_or_create_customer.assert_not_called()
    stripe_service.create_checkout_session.assert_not_called()

    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# CUSTOMER INFORMATION
# ============================================================


def test_missing_customer_email_is_rejected(
    use_case,
    application_repo,
    payment_repo,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application(
        email=None,
    )

    payment_repo.get_by_application_and_status.return_value = None

    dto = make_dto()

    with pytest.raises(
        PaymentNotAllowed,
        match="adresse email",
    ):
        use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()


def test_missing_customer_name_is_rejected(
    use_case,
    application_repo,
    payment_repo,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application(
        first_name=None,
        last_name=None,
    )

    payment_repo.get_by_application_and_status.return_value = None

    dto = make_dto()

    with pytest.raises(
        PaymentNotAllowed,
        match="nom du client",
    ):
        use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()


def test_customer_name_is_built_from_first_and_last_name(
    use_case,
    application_repo,
    payment_repo,
    stripe_service,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application(
        first_name="leila",
        last_name="el",
    )

    payment_repo.get_by_application_and_status.return_value = None

    dto = make_dto()

    with patch(
        "modules.payments.application.use_cases.create_checkout_session.settings"
    ) as settings:
        settings.SUCCESS_URL = "http://success"
        settings.CANCEL_URL = "http://cancel"

        use_case.execute(dto)

    stripe_service.get_or_create_customer.assert_called_once_with(
        email="leila@example.com",
        name="leila el",
    )


# ============================================================
# PRODUCT NAME
# ============================================================


def test_product_name_uses_vehicle_brand_and_model(
    use_case,
):
    application = make_application(
        vehicle=make_vehicle(
            brand="Audi",
            model="A3",
        ),
    )

    assert (
        use_case._build_product_name(application)
        == "Audi A3"
    )


@pytest.mark.parametrize(
    "brand,model",
    [
        (None, "A3"),
        ("Audi", None),
        ("", "A3"),
        ("Audi", ""),
    ],
)
def test_product_name_handles_missing_brand_or_model(
    brand,
    model,
    use_case,
):
    application = make_application(
        vehicle=make_vehicle(
            brand=brand,
            model=model,
        ),
    )

    result = use_case._build_product_name(
        application
    )

    assert result in {
        "A3",
        "Audi",
        "Paiement M-Motors",
    }


def test_product_name_falls_back_when_vehicle_has_no_brand_or_model(
    use_case,
    application_repo,
    stripe_service,
    payment_repo,
):
    application = make_application()

    application.vehicle.brand = ""
    application.vehicle.model = ""

    application_repo.get_by_id.return_value = application

    payment_repo.get_by_application_and_status.return_value = None

    dto = make_dto()

    use_case.execute(dto)

    stripe_service.create_checkout_session.assert_called_once()

    assert (
        stripe_service.create_checkout_session.call_args.kwargs[
            "product_name"
        ]
        == "Paiement M-Motors"
    )


def test_product_name_falls_back_when_brand_and_model_are_empty(
    use_case,
):
    application = make_application(
        vehicle=make_vehicle(
            brand="",
            model="",
        ),
    )

    assert (
        use_case._build_product_name(application)
        == "Paiement M-Motors"
    )


# ============================================================
# STRIPE CUSTOMER
# ============================================================


def test_stripe_customer_is_created_or_retrieved(
    use_case,
    application_repo,
    payment_repo,
    stripe_service,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application()

    payment_repo.get_by_application_and_status.return_value = None

    dto = make_dto()

    with patch(
        "modules.payments.application.use_cases.create_checkout_session.settings"
    ) as settings:
        settings.SUCCESS_URL = "http://success"
        settings.CANCEL_URL = "http://cancel"

        use_case.execute(dto)

    stripe_service.get_or_create_customer.assert_called_once_with(
        email="leila@example.com",
        name="leila el",
    )


# ============================================================
# STRIPE CHECKOUT SESSION
# ============================================================


def test_stripe_checkout_session_is_created(
    use_case,
    application_repo,
    payment_repo,
    stripe_service,
):
    application_repo.get_by_id.return_value = make_application(
        total_price=1200,
    )

    payment_repo.get_by_application_and_status.return_value = None

    dto = make_dto()

    with patch(
        "modules.payments.application.use_cases.create_checkout_session.settings"
    ) as settings:
        settings.SUCCESS_URL = "http://success"
        settings.CANCEL_URL = "http://cancel"

        use_case.execute(dto)

    stripe_service.create_checkout_session.assert_called_once()

    call_args = (
        stripe_service.create_checkout_session.call_args.kwargs
    )

    assert call_args["application_id"] == "application-1"
    assert call_args["amount"] == 1200
    assert call_args["product_name"] == "BMW Serie 3"
    assert call_args["success_url"] == "http://success"
    assert call_args["cancel_url"] == "http://cancel"
    assert call_args["customer_id"] == "cus-1"


# ============================================================
# PAYMENT CREATION
# ============================================================


def test_new_payment_is_created_when_no_pending_or_failed_payment_exists(
    use_case,
    application_repo,
    payment_repo,
    stripe_service,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application(
        total_price=1200,
    )

    payment_repo.get_by_application_and_status.return_value = None

    dto = make_dto()

    with patch(
        "modules.payments.application.use_cases.create_checkout_session.settings"
    ) as settings:
        settings.SUCCESS_URL = "http://success"
        settings.CANCEL_URL = "http://cancel"

        result = use_case.execute(dto)

    payment_repo.save.assert_called_once()

    payment = payment_repo.save.call_args.args[0]

    assert payment.application_id == "application-1"
    assert payment.user_id == "user-1"
    assert payment.amount == 1200
    assert payment.currency == "eur"
    assert payment.stripe_customer_id == "cus-1"
    assert payment.stripe_session_id == "session-1"
    assert payment.stripe_payment_intent_id is None
    assert payment.status == PaymentStatus.PENDING
    assert payment.description == "BMW Serie 3"

    assert result.payment_id == payment.id


# ============================================================
# EXISTING PENDING PAYMENT
# ============================================================


def test_existing_pending_payment_is_updated(
    use_case,
    application_repo,
    payment_repo,
    stripe_service,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application(
        total_price=1500,
    )

    pending_payment = make_payment(
        payment_id="pending-1",
        status=PaymentStatus.PENDING,
        amount=500,
    )

    def get_payment(
        application_id,
        status,
    ):
        if status == PaymentStatus.PAID:
            return None

        if status == PaymentStatus.PENDING:
            return pending_payment

        return None

    payment_repo.get_by_application_and_status.side_effect = (
        get_payment
    )

    dto = make_dto()

    with patch(
        "modules.payments.application.use_cases.create_checkout_session.settings"
    ) as settings:
        settings.SUCCESS_URL = "http://success"
        settings.CANCEL_URL = "http://cancel"

        result = use_case.execute(dto)

    payment_repo.update.assert_called_once_with(
        pending_payment
    )

    assert pending_payment.amount == 1500
    assert pending_payment.stripe_customer_id == "cus-1"
    assert pending_payment.stripe_session_id == "session-1"
    assert pending_payment.stripe_payment_intent_id is None
    assert pending_payment.status == PaymentStatus.PENDING
    assert pending_payment.description == "BMW Serie 3"

    assert result.payment_id == "pending-1"


# ============================================================
# EXISTING FAILED PAYMENT
# ============================================================


def test_existing_failed_payment_is_reused_and_updated(
    use_case,
    application_repo,
    payment_repo,
    stripe_service,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application(
        total_price=1800,
    )

    failed_payment = make_payment(
        payment_id="failed-1",
        status=PaymentStatus.FAILED,
        amount=500,
    )

    def get_payment(
        application_id,
        status,
    ):
        if status == PaymentStatus.PAID:
            return None

        if status == PaymentStatus.PENDING:
            return None

        if status == PaymentStatus.FAILED:
            return failed_payment

        return None

    payment_repo.get_by_application_and_status.side_effect = (
        get_payment
    )

    dto = make_dto()

    with patch(
        "modules.payments.application.use_cases.create_checkout_session.settings"
    ) as settings:
        settings.SUCCESS_URL = "http://success"
        settings.CANCEL_URL = "http://cancel"

        result = use_case.execute(dto)

    payment_repo.update.assert_called_once_with(
        failed_payment
    )

    assert failed_payment.amount == 1800
    assert failed_payment.status == PaymentStatus.PENDING
    assert failed_payment.stripe_customer_id == "cus-1"
    assert failed_payment.stripe_session_id == "session-1"

    assert result.payment_id == "failed-1"


# ============================================================
# EVENT
# ============================================================


def test_payment_initiated_event_is_logged(
    use_case,
    application_repo,
    payment_repo,
    event_service,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application(
        total_price=1200,
    )

    payment_repo.get_by_application_and_status.return_value = None

    dto = make_dto()

    with patch(
        "modules.payments.application.use_cases.create_checkout_session.settings"
    ) as settings:
        settings.SUCCESS_URL = "http://success"
        settings.CANCEL_URL = "http://cancel"

        use_case.execute(dto)

    event_service.log.assert_called_once()

    call_args = event_service.log.call_args.kwargs

    assert call_args["type"] == EventType.PAYMENT_INITIATED
    assert call_args["message"] == "Paiement initialisé"
    assert call_args["user_id"] == "user-1"
    assert call_args["application_id"] == "application-1"
    assert call_args["vehicle_id"] == "vehicle-1"

    assert call_args["event_metadata"]["amount"] == 1200
    assert (
        call_args["event_metadata"]["stripe_session_id"]
        == "session-1"
    )
    assert (
        call_args["event_metadata"]["stripe_customer_id"]
        == "cus-1"
    )


# ============================================================
# COMMIT
# ============================================================


def test_successful_checkout_commits(
    use_case,
    application_repo,
    payment_repo,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application()

    payment_repo.get_by_application_and_status.return_value = None

    dto = make_dto()

    with patch(
        "modules.payments.application.use_cases.create_checkout_session.settings"
    ) as settings:
        settings.SUCCESS_URL = "http://success"
        settings.CANCEL_URL = "http://cancel"

        use_case.execute(dto)

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# RESULT
# ============================================================


def test_successful_checkout_returns_result(
    use_case,
    application_repo,
    payment_repo,
):
    application_repo.get_by_id.return_value = make_application()

    payment_repo.get_by_application_and_status.return_value = None

    dto = make_dto()

    with patch(
        "modules.payments.application.use_cases.create_checkout_session.settings"
    ) as settings:
        settings.SUCCESS_URL = "http://success"
        settings.CANCEL_URL = "http://cancel"

        result = use_case.execute(dto)

    assert isinstance(
        result,
        CreateCheckoutSessionResult,
    )

    assert (
        result.checkout_url
        == "https://checkout.stripe.com/session-1"
    )

    assert result.payment_id is not None


# ============================================================
# ROLLBACK / ERRORS
# ============================================================


def test_stripe_customer_error_rolls_back(
    use_case,
    application_repo,
    payment_repo,
    stripe_service,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application()

    payment_repo.get_by_application_and_status.return_value = None

    stripe_service.get_or_create_customer.side_effect = (
        RuntimeError("stripe customer error")
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="stripe customer error",
    ):
        use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_stripe_session_error_rolls_back(
    use_case,
    application_repo,
    payment_repo,
    stripe_service,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application()

    payment_repo.get_by_application_and_status.return_value = None

    stripe_service.create_checkout_session.side_effect = (
        RuntimeError("stripe session error")
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="stripe session error",
    ):
        use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_payment_save_error_rolls_back(
    use_case,
    application_repo,
    payment_repo,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application()

    payment_repo.get_by_application_and_status.return_value = None

    payment_repo.save.side_effect = RuntimeError(
        "payment save error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="payment save error",
    ):
        use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_event_error_rolls_back(
    use_case,
    application_repo,
    payment_repo,
    event_service,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application()

    payment_repo.get_by_application_and_status.return_value = None

    event_service.log.side_effect = RuntimeError(
        "event error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="event error",
    ):
        use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_commit_error_rolls_back(
    use_case,
    application_repo,
    payment_repo,
    unit_of_work,
):
    application_repo.get_by_id.return_value = make_application()

    payment_repo.get_by_application_and_status.return_value = None

    unit_of_work.commit.side_effect = RuntimeError(
        "commit error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="commit error",
    ):
        use_case.execute(dto)

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()