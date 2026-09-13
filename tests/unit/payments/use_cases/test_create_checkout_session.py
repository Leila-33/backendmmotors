import pytest
from unittest.mock import Mock, patch

from modules.applications.domain.enums import (
    ApplicationStatus,
    EventType,
)
from modules.applications.domain.exceptions import (
    ApplicationNotFound,
)
from modules.payments.domain.enums import PaymentStatus
from modules.payments.domain.exceptions import PaymentNotAllowed

from modules.payments.application.dtos.create_checkout_session_dto import (
    CreateCheckoutSessionDTO,
)
from modules.payments.application.results.create_checkout_session_result import (
    CreateCheckoutSessionResult,
)

from modules.payments.application.use_cases.create_checkout_session import (
    CreateCheckoutSessionUseCase,
)


@pytest.fixture
def payment_repository():
    return Mock()


@pytest.fixture
def stripe_service():
    return Mock()


@pytest.fixture
def application_repository():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    payment_repository,
    stripe_service,
    application_repository,
    event_service,
    unit_of_work,
):
    return CreateCheckoutSessionUseCase(
        payment_repository=payment_repository,
        stripe_service=stripe_service,
        application_repository=application_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


def make_dto(
    application_id="application-123",
    user_id="user-123",
    email="client@example.com",
    customer_name="Jean Dupont",
    amount=15000,
    product_name="Peugeot 208",
):
    return CreateCheckoutSessionDTO(
        application_id=application_id,
        user_id=user_id,
        email=email,
        customer_name=customer_name,
        amount=amount,
        product_name=product_name,
    )


def make_application(
    application_id="application-123",
    user_id="user-123",
    vehicle_id="vehicle-123",
    status=ApplicationStatus.APPROVED,
):
    application = Mock()

    application.id = application_id
    application.user_id = user_id
    application.vehicle_id = vehicle_id
    application.status = status

    return application


def make_stripe_session(
    session_id="cs_test_123",
    url="https://checkout.stripe.com/test",
):
    session = Mock()
    session.id = session_id
    session.url = url

    return session


def make_payment(
    payment_id="payment-123",
    amount=15000,
    status=PaymentStatus.PENDING,
):
    payment = Mock()

    payment.id = payment_id
    payment.amount = amount
    payment.status = status

    return payment


def test_create_checkout_session_success_creates_payment(
    use_case,
    payment_repository,
    stripe_service,
    application_repository,
    event_service,
    unit_of_work,
):
    application = make_application()
    dto = make_dto()

    application_repository.get_by_id.return_value = application

    # Aucun paiement PAID
    payment_repository.get_by_application_and_status.side_effect = [
        None,  # PAID
        None,  # PENDING
        None,  # FAILED
    ]

    stripe_service.get_or_create_customer.return_value = "cus-123"

    stripe_service.create_checkout_session.return_value = (
        make_stripe_session()
    )

    with patch(
        "modules.payments.application.use_cases.create_checkout_session.uuid4",
        return_value="payment-123",
    ), patch(
        "modules.payments.application.use_cases.create_checkout_session.Payment"
    ) as payment_class:

        payment = make_payment()

        payment_class.return_value = payment

        result = use_case.execute(dto)

    application_repository.get_by_id.assert_called_once_with(
        "application-123"
    )

    stripe_service.get_or_create_customer.assert_called_once_with(
        email="client@example.com",
        name="Jean Dupont",
    )

    stripe_service.create_checkout_session.assert_called_once_with(
        application_id="application-123",
        amount=15000,
        product_name="Peugeot 208",
        success_url=__import__(
            "core.config.settings",
            fromlist=["settings"],
        ).settings.SUCCESS_URL,
        cancel_url=__import__(
            "core.config.settings",
            fromlist=["settings"],
        ).settings.CANCEL_URL,
        customer_id="cus-123",
    )

    payment_class.assert_called_once()

    payment_repository.save.assert_called_once_with(
        payment
    )

    payment_repository.update.assert_not_called()

    event_service.log.assert_called_once_with(
        type=EventType.PAYMENT_INITIATED,
        message="Paiement initialisé",
        user_id="user-123",
        application_id="application-123",
        vehicle_id="vehicle-123",
        event_metadata={
            "payment_id": "payment-123",
            "amount": 15000,
            "stripe_session_id": "cs_test_123",
            "stripe_customer_id": "cus-123",
        },
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()

    assert isinstance(
        result,
        CreateCheckoutSessionResult,
    )

    assert result.checkout_url == (
        "https://checkout.stripe.com/test"
    )

    assert result.payment_id == "payment-123"


def test_create_checkout_session_raises_when_application_not_found(
    use_case,
    application_repository,
    payment_repository,
    stripe_service,
    event_service,
    unit_of_work,
):
    dto = make_dto()

    application_repository.get_by_id.return_value = None

    with pytest.raises(ApplicationNotFound):
        use_case.execute(dto)

    application_repository.get_by_id.assert_called_once_with(
        "application-123"
    )

    payment_repository.get_by_application_and_status.assert_not_called()
    stripe_service.get_or_create_customer.assert_not_called()
    stripe_service.create_checkout_session.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


@pytest.mark.parametrize(
    "status",
    [
        ApplicationStatus.DRAFT,
        ApplicationStatus.REJECTED,
    ],
)
def test_create_checkout_session_rejects_application_with_invalid_status(
    use_case,
    application_repository,
    payment_repository,
    stripe_service,
    event_service,
    unit_of_work,
    status,
):
    application = make_application(
        status=status
    )

    application_repository.get_by_id.return_value = application

    dto = make_dto()

    with pytest.raises(PaymentNotAllowed):
        use_case.execute(dto)

    payment_repository.get_by_application_and_status.assert_not_called()
    stripe_service.get_or_create_customer.assert_not_called()
    stripe_service.create_checkout_session.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_create_checkout_session_returns_existing_paid_payment(
    use_case,
    application_repository,
    payment_repository,
    stripe_service,
    event_service,
    unit_of_work,
):
    application = make_application()

    paid_payment = make_payment(
        payment_id="payment-paid",
        status=PaymentStatus.PAID,
    )

    application_repository.get_by_id.return_value = application

    payment_repository.get_by_application_and_status.return_value = (
        paid_payment
    )

    dto = make_dto()

    result = use_case.execute(dto)

    payment_repository.get_by_application_and_status.assert_called_once_with(
        "application-123",
        PaymentStatus.PAID,
    )

    stripe_service.get_or_create_customer.assert_not_called()
    stripe_service.create_checkout_session.assert_not_called()

    payment_repository.save.assert_not_called()
    payment_repository.update.assert_not_called()

    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_not_called()

    assert isinstance(
        result,
        CreateCheckoutSessionResult,
    )

    assert result.checkout_url is None
    assert result.payment_id == "payment-paid"


def test_create_checkout_session_updates_existing_pending_payment(
    use_case,
    application_repository,
    payment_repository,
    stripe_service,
    event_service,
    unit_of_work,
):
    application = make_application()
    payment = make_payment(
        payment_id="payment-pending",
        status=PaymentStatus.PENDING,
    )

    application_repository.get_by_id.return_value = application

    payment_repository.get_by_application_and_status.side_effect = [
        None,      # PAID
        payment,   # PENDING
    ]

    stripe_service.get_or_create_customer.return_value = "cus-456"

    stripe_service.create_checkout_session.return_value = (
        make_stripe_session(
            session_id="cs-456",
            url="https://checkout.stripe.com/456",
        )
    )

    dto = make_dto()

    result = use_case.execute(dto)

    assert payment.stripe_customer_id == "cus-456"
    assert payment.stripe_session_id == "cs-456"
    assert payment.stripe_payment_intent_id is None
    assert payment.status == PaymentStatus.PENDING

    payment_repository.update.assert_called_once_with(
        payment
    )

    payment_repository.save.assert_not_called()

    event_service.log.assert_called_once_with(
        type=EventType.PAYMENT_INITIATED,
        message="Paiement initialisé",
        user_id="user-123",
        application_id="application-123",
        vehicle_id="vehicle-123",
        event_metadata={
            "payment_id": "payment-pending",
            "amount": payment.amount,
            "stripe_session_id": "cs-456",
            "stripe_customer_id": "cus-456",
        },
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()

    assert result.checkout_url == (
        "https://checkout.stripe.com/456"
    )
    assert result.payment_id == "payment-pending"


def test_create_checkout_session_updates_existing_failed_payment(
    use_case,
    application_repository,
    payment_repository,
    stripe_service,
    unit_of_work,
):
    application = make_application()

    payment = make_payment(
        payment_id="payment-failed",
        status=PaymentStatus.FAILED,
    )

    application_repository.get_by_id.return_value = application

    payment_repository.get_by_application_and_status.side_effect = [
        None,      # PAID
        None,      # PENDING
        payment,   # FAILED
    ]

    stripe_service.get_or_create_customer.return_value = "cus-789"

    stripe_service.create_checkout_session.return_value = (
        make_stripe_session(
            session_id="cs-789",
            url="https://checkout.stripe.com/789",
        )
    )

    result = use_case.execute(
        make_dto()
    )

    assert payment.stripe_customer_id == "cus-789"
    assert payment.stripe_session_id == "cs-789"
    assert payment.stripe_payment_intent_id is None
    assert payment.status == PaymentStatus.PENDING

    payment_repository.update.assert_called_once_with(
        payment
    )

    payment_repository.save.assert_not_called()

    unit_of_work.commit.assert_called_once()

    assert result.payment_id == "payment-failed"
    assert result.checkout_url == (
        "https://checkout.stripe.com/789"
    )


def test_create_checkout_session_creates_customer_and_session(
    use_case,
    application_repository,
    payment_repository,
    stripe_service,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    payment_repository.get_by_application_and_status.side_effect = [
        None,
        None,
        None,
    ]

    stripe_service.get_or_create_customer.return_value = (
        "cus-new"
    )

    stripe_service.create_checkout_session.return_value = (
        make_stripe_session()
    )

    with patch(
        "modules.payments.application.use_cases.create_checkout_session.Payment"
    ) as payment_class:

        payment = make_payment()
        payment_class.return_value = payment

        use_case.execute(
            make_dto(
                email="test@example.com",
                customer_name="Alice Martin",
            )
        )

    stripe_service.get_or_create_customer.assert_called_once_with(
        email="test@example.com",
        name="Alice Martin",
    )

    stripe_service.create_checkout_session.assert_called_once()

    call_kwargs = (
        stripe_service
        .create_checkout_session
        .call_args.kwargs
    )

    assert call_kwargs["application_id"] == "application-123"
    assert call_kwargs["amount"] == 15000
    assert call_kwargs["product_name"] == "Peugeot 208"
    assert call_kwargs["customer_id"] == "cus-new"


def test_create_checkout_session_rolls_back_when_payment_save_fails(
    use_case,
    application_repository,
    payment_repository,
    stripe_service,
    event_service,
    unit_of_work,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    payment_repository.get_by_application_and_status.side_effect = [
        None,
        None,
        None,
    ]

    stripe_service.get_or_create_customer.return_value = "cus-123"

    stripe_service.create_checkout_session.return_value = (
        make_stripe_session()
    )

    payment_repository.save.side_effect = RuntimeError(
        "Database error"
    )

    with patch(
        "modules.payments.application.use_cases.create_checkout_session.Payment"
    ) as payment_class:

        payment_class.return_value = make_payment()

        with pytest.raises(
            RuntimeError,
            match="Database error",
        ):
            use_case.execute(make_dto())

    payment_repository.save.assert_called_once()

    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_create_checkout_session_rolls_back_when_event_fails(
    use_case,
    application_repository,
    payment_repository,
    stripe_service,
    event_service,
    unit_of_work,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    payment_repository.get_by_application_and_status.side_effect = [
        None,
        None,
        None,
    ]

    stripe_service.get_or_create_customer.return_value = "cus-123"

    stripe_service.create_checkout_session.return_value = (
        make_stripe_session()
    )

    payment = make_payment()

    with patch(
        "modules.payments.application.use_cases.create_checkout_session.Payment"
    ) as payment_class:

        payment_class.return_value = payment

        event_service.log.side_effect = RuntimeError(
            "Event error"
        )

        with pytest.raises(
            RuntimeError,
            match="Event error",
        ):
            use_case.execute(make_dto())

    payment_repository.save.assert_called_once_with(
        payment
    )

    event_service.log.assert_called_once()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_create_checkout_session_rolls_back_when_commit_fails(
    use_case,
    application_repository,
    payment_repository,
    stripe_service,
    event_service,
    unit_of_work,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    payment_repository.get_by_application_and_status.side_effect = [
        None,
        None,
        None,
    ]

    stripe_service.get_or_create_customer.return_value = "cus-123"

    stripe_service.create_checkout_session.return_value = (
        make_stripe_session()
    )

    payment = make_payment()

    with patch(
        "modules.payments.application.use_cases.create_checkout_session.Payment"
    ) as payment_class:

        payment_class.return_value = payment

        unit_of_work.commit.side_effect = RuntimeError(
            "Commit error"
        )

        with pytest.raises(
            RuntimeError,
            match="Commit error",
        ):
            use_case.execute(make_dto())

    payment_repository.save.assert_called_once_with(
        payment
    )

    event_service.log.assert_called_once()

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()