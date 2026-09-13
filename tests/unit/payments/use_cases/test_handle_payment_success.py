import pytest
from unittest.mock import Mock

from modules.applications.domain.enums import EventType
from modules.applications.domain.exceptions import ApplicationNotFound

from modules.payments.domain.enums import PaymentStatus
from modules.payments.domain.exceptions import (
    PaymentNotFound,
    PaymentInvalid,
)

from modules.vehicles.domain.enums import VehicleType

from modules.payments.application.dtos.handle_payment_success_dto import (
    HandlePaymentSuccessDTO,
)

from modules.payments.application.dtos.complete_sale_payment_dto import (
    CompleteSalePaymentDTO,
)

from modules.payments.application.dtos.complete_rental_payment_dto import (
    CompleteRentalPaymentDTO,
)

from modules.payments.application.results.handle_payment_success_result import (
    HandlePaymentSuccessResult,
)

from modules.payments.application.use_cases.handle_payment_success import (
    HandlePaymentSuccessUseCase,
)


@pytest.fixture
def payment_repository():
    return Mock()


@pytest.fixture
def application_repository():
    return Mock()


@pytest.fixture
def complete_sale_payment_uc():
    return Mock()


@pytest.fixture
def complete_rental_payment_uc():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def stripe_service():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    payment_repository,
    application_repository,
    complete_sale_payment_uc,
    complete_rental_payment_uc,
    event_service,
    stripe_service,
    unit_of_work,
):
    return HandlePaymentSuccessUseCase(
        payment_repository=payment_repository,
        application_repository=application_repository,
        complete_sale_payment_uc=complete_sale_payment_uc,
        complete_rental_payment_uc=complete_rental_payment_uc,
        event_service=event_service,
        stripe_service=stripe_service,
        unit_of_work=unit_of_work,
    )


def make_dto(
    stripe_session_id="cs_test_123",
    stripe_payment_intent_id="pi_test_123",
):
    return HandlePaymentSuccessDTO(
        stripe_session_id=stripe_session_id,
        stripe_payment_intent_id=stripe_payment_intent_id,
    )


def make_vehicle(
    vehicle_type=VehicleType.SALE,
    vehicle_id="vehicle-123",
):
    vehicle = Mock()

    vehicle.id = vehicle_id
    vehicle.type = vehicle_type

    return vehicle


def make_application(
    application_id="application-123",
    user_id="user-123",
    vehicle=None,
):
    application = Mock()

    application.id = application_id
    application.user_id = user_id
    application.vehicle = vehicle
    application.vehicle_id = vehicle.id if vehicle else "vehicle-123"

    return application


def make_payment(
    payment_id="payment-123",
    application_id="application-123",
    status=PaymentStatus.PENDING,
    amount=15000,
    stripe_customer_id="cus-123",
):
    payment = Mock()

    payment.id = payment_id
    payment.application_id = application_id
    payment.status = status
    payment.amount = amount
    payment.stripe_customer_id = stripe_customer_id
    payment.stripe_payment_intent_id = None
    payment.paid_at = None

    return payment


def configure_payment_and_application(
    payment_repository,
    application_repository,
    payment,
    application,
):
    payment_repository.get_by_session_id.return_value = payment
    application_repository.get_by_id.return_value = application


def test_execute_success_for_sale(
    use_case,
    payment_repository,
    application_repository,
    complete_sale_payment_uc,
    complete_rental_payment_uc,
    event_service,
    stripe_service,
    unit_of_work,
):
    vehicle = make_vehicle(
        vehicle_type=VehicleType.SALE,
    )

    application = make_application(
        vehicle=vehicle,
    )

    payment = make_payment()

    configure_payment_and_application(
        payment_repository,
        application_repository,
        payment,
        application,
    )

    dto = make_dto()

    result = use_case.execute(dto)

    assert isinstance(
        result,
        HandlePaymentSuccessResult,
    )

    assert result.payment_id == "payment-123"
    assert result.status == PaymentStatus.PAID.value
    assert result.vehicle_type == VehicleType.SALE.value
    assert result.application_id == "application-123"
    assert result.message == "Paiement traité avec succès"

    assert payment.stripe_payment_intent_id == "pi_test_123"
    assert payment.status == PaymentStatus.PAID
    assert payment.paid_at is not None

    assert payment.paid_at.tzinfo is not None

    stripe_service.set_customer_default_payment_method.assert_called_once_with(
        customer_id="cus-123",
        payment_intent_id="pi_test_123",
    )

    payment_repository.update.assert_called_once_with(
        payment
    )

    complete_sale_payment_uc.execute.assert_called_once()

    sale_dto = (
        complete_sale_payment_uc.execute.call_args.args[0]
    )

    assert isinstance(
        sale_dto,
        CompleteSalePaymentDTO,
    )

    assert sale_dto.application_id == "application-123"
    assert sale_dto.payment_id == "payment-123"

    complete_rental_payment_uc.execute.assert_not_called()

    event_service.log.assert_called_once_with(
        type=EventType.PAYMENT_SUCCEEDED,
        message="Paiement confirmé",
        application_id="application-123",
        user_id="user-123",
        vehicle_id="vehicle-123",
        event_metadata={
            "payment_id": "payment-123",
            "amount": 15000,
            "vehicle_type": VehicleType.SALE.value,
            "stripe_session_id": "cs_test_123",
            "stripe_customer_id": "cus-123",
            "stripe_payment_intent_id": "pi_test_123",
        },
    )

    unit_of_work.commit.assert_called_once_with()
    unit_of_work.rollback.assert_not_called()


def test_execute_success_for_rental(
    use_case,
    payment_repository,
    application_repository,
    complete_sale_payment_uc,
    complete_rental_payment_uc,
    event_service,
    stripe_service,
    unit_of_work,
):
    vehicle = make_vehicle(
        vehicle_type=VehicleType.RENT,
    )

    application = make_application(
        vehicle=vehicle,
    )

    payment = make_payment()

    configure_payment_and_application(
        payment_repository,
        application_repository,
        payment,
        application,
    )

    dto = make_dto()

    result = use_case.execute(dto)

    assert result.payment_id == "payment-123"
    assert result.status == PaymentStatus.PAID.value
    assert result.vehicle_type == VehicleType.RENT.value

    complete_rental_payment_uc.execute.assert_called_once()

    rental_dto = (
        complete_rental_payment_uc.execute.call_args.args[0]
    )

    assert isinstance(
        rental_dto,
        CompleteRentalPaymentDTO,
    )

    assert rental_dto.application_id == "application-123"
    assert rental_dto.payment_id == "payment-123"

    complete_sale_payment_uc.execute.assert_not_called()

    event_service.log.assert_called_once()

    unit_of_work.commit.assert_called_once_with()
    unit_of_work.rollback.assert_not_called()


def test_execute_raises_when_payment_not_found(
    use_case,
    payment_repository,
    application_repository,
    stripe_service,
    event_service,
    unit_of_work,
):
    payment_repository.get_by_session_id.return_value = None

    dto = make_dto()

    with pytest.raises(PaymentNotFound):
        use_case.execute(dto)

    payment_repository.get_by_session_id.assert_called_once_with(
        "cs_test_123"
    )

    application_repository.get_by_id.assert_not_called()
    stripe_service.set_customer_default_payment_method.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


def test_execute_raises_when_application_not_found(
    use_case,
    payment_repository,
    application_repository,
    stripe_service,
    event_service,
    unit_of_work,
):
    payment = make_payment()

    payment_repository.get_by_session_id.return_value = payment
    application_repository.get_by_id.return_value = None

    dto = make_dto()

    with pytest.raises(ApplicationNotFound):
        use_case.execute(dto)

    application_repository.get_by_id.assert_called_once_with(
        "application-123"
    )

    stripe_service.set_customer_default_payment_method.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


def test_execute_is_idempotent_when_payment_already_paid(
    use_case,
    payment_repository,
    application_repository,
    complete_sale_payment_uc,
    complete_rental_payment_uc,
    event_service,
    stripe_service,
    unit_of_work,
):
    vehicle = make_vehicle(
        vehicle_type=VehicleType.SALE,
    )

    application = make_application(
        vehicle=vehicle,
    )

    payment = make_payment(
        status=PaymentStatus.PAID,
    )

    configure_payment_and_application(
        payment_repository,
        application_repository,
        payment,
        application,
    )

    dto = make_dto()

    result = use_case.execute(dto)

    assert isinstance(
        result,
        HandlePaymentSuccessResult,
    )

    assert result.payment_id == "payment-123"
    assert result.status == PaymentStatus.PAID.value
    assert result.vehicle_type == VehicleType.SALE.value
    assert result.application_id == "application-123"
    assert result.message == "Paiement déjà traité"

    stripe_service.set_customer_default_payment_method.assert_not_called()
    payment_repository.update.assert_not_called()

    complete_sale_payment_uc.execute.assert_not_called()
    complete_rental_payment_uc.execute.assert_not_called()

    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_not_called()


def test_execute_raises_when_stripe_customer_is_missing(
    use_case,
    payment_repository,
    application_repository,
    stripe_service,
    unit_of_work,
):
    vehicle = make_vehicle()

    application = make_application(
        vehicle=vehicle,
    )

    payment = make_payment(
        stripe_customer_id=None,
    )

    configure_payment_and_application(
        payment_repository,
        application_repository,
        payment,
        application,
    )

    dto = make_dto()

    with pytest.raises(
        PaymentInvalid,
        match="Customer Stripe absent du paiement.",
    ):
        use_case.execute(dto)

    stripe_service.set_customer_default_payment_method.assert_not_called()
    payment_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


def test_execute_raises_when_payment_intent_is_missing(
    use_case,
    payment_repository,
    application_repository,
    stripe_service,
    unit_of_work,
):
    vehicle = make_vehicle()

    application = make_application(
        vehicle=vehicle,
    )

    payment = make_payment()

    configure_payment_and_application(
        payment_repository,
        application_repository,
        payment,
        application,
    )

    dto = make_dto(
        stripe_payment_intent_id=None,
    )

    with pytest.raises(
        PaymentInvalid,
        match="PaymentIntent Stripe absent du paiement.",
    ):
        use_case.execute(dto)

    stripe_service.set_customer_default_payment_method.assert_not_called()
    payment_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


def test_execute_rolls_back_when_stripe_service_fails(
    use_case,
    payment_repository,
    application_repository,
    stripe_service,
    complete_sale_payment_uc,
    event_service,
    unit_of_work,
):
    vehicle = make_vehicle()

    application = make_application(
        vehicle=vehicle,
    )

    payment = make_payment()

    configure_payment_and_application(
        payment_repository,
        application_repository,
        payment,
        application,
    )

    stripe_service.set_customer_default_payment_method.side_effect = (
        RuntimeError("Stripe error")
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="Stripe error",
    ):
        use_case.execute(dto)

    payment_repository.update.assert_not_called()
    complete_sale_payment_uc.execute.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


def test_execute_rolls_back_when_payment_update_fails(
    use_case,
    payment_repository,
    application_repository,
    stripe_service,
    complete_sale_payment_uc,
    event_service,
    unit_of_work,
):
    vehicle = make_vehicle()

    application = make_application(
        vehicle=vehicle,
    )

    payment = make_payment()

    configure_payment_and_application(
        payment_repository,
        application_repository,
        payment,
        application,
    )

    payment_repository.update.side_effect = (
        RuntimeError("Update error")
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="Update error",
    ):
        use_case.execute(dto)

    payment_repository.update.assert_called_once_with(
        payment
    )

    complete_sale_payment_uc.execute.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


def test_execute_rolls_back_when_completion_use_case_fails(
    use_case,
    payment_repository,
    application_repository,
    complete_sale_payment_uc,
    event_service,
    unit_of_work,
):
    vehicle = make_vehicle(
        vehicle_type=VehicleType.SALE,
    )

    application = make_application(
        vehicle=vehicle,
    )

    payment = make_payment()

    configure_payment_and_application(
        payment_repository,
        application_repository,
        payment,
        application,
    )

    complete_sale_payment_uc.execute.side_effect = (
        RuntimeError("Sale completion error")
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="Sale completion error",
    ):
        use_case.execute(dto)

    payment_repository.update.assert_called_once_with(
        payment
    )

    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


def test_execute_rolls_back_when_event_fails(
    use_case,
    payment_repository,
    application_repository,
    complete_sale_payment_uc,
    event_service,
    unit_of_work,
):
    vehicle = make_vehicle()

    application = make_application(
        vehicle=vehicle,
    )

    payment = make_payment()

    configure_payment_and_application(
        payment_repository,
        application_repository,
        payment,
        application,
    )

    event_service.log.side_effect = (
        RuntimeError("Event error")
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="Event error",
    ):
        use_case.execute(dto)

    payment_repository.update.assert_called_once_with(
        payment
    )

    complete_sale_payment_uc.execute.assert_called_once()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


def test_execute_rolls_back_when_commit_fails(
    use_case,
    payment_repository,
    application_repository,
    complete_sale_payment_uc,
    event_service,
    unit_of_work,
):
    vehicle = make_vehicle()

    application = make_application(
        vehicle=vehicle,
    )

    payment = make_payment()

    configure_payment_and_application(
        payment_repository,
        application_repository,
        payment,
        application,
    )

    unit_of_work.commit.side_effect = (
        RuntimeError("Commit error")
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="Commit error",
    ):
        use_case.execute(dto)

    payment_repository.update.assert_called_once_with(
        payment

    )

    complete_sale_payment_uc.execute.assert_called_once()

    event_service.log.assert_called_once()

    unit_of_work.commit.assert_called_once_with()
    unit_of_work.rollback.assert_called_once_with()