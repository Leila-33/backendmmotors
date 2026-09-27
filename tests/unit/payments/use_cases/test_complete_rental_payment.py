from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from modules.applications.domain.enums import (
    ApplicationStatus,
    EventType,
)
from modules.applications.domain.exceptions import (
    ApplicationNotFound,
)

from modules.payments.application.dtos.complete_rental_payment_dto import (
    CompleteRentalPaymentDTO,
)
from modules.payments.application.results.complete_rental_payment_result import (
    CompleteRentalPaymentResult,
)

from modules.payments.application.use_cases.complete_rental_payment import (
    CompleteRentalPaymentUseCase,
)


# ============================================================
# HELPERS
# ============================================================


def make_vehicle(
    *,
    vehicle_id="vehicle-1",
):
    return SimpleNamespace(
        id=vehicle_id,
    )


def make_application(
    *,
    application_id="application-1",
    user_id="user-1",
    status=None,
    vehicle=None,
):
    if status is None:
        status = ApplicationStatus.APPROVED

    if vehicle is None:
        vehicle = make_vehicle()

    return SimpleNamespace(
        id=application_id,
        user_id=user_id,
        status=status,
        vehicle=vehicle,
    )


def make_dto(
    *,
    application_id="application-1",
    payment_id="payment-1",
):
    return CompleteRentalPaymentDTO(
        application_id=application_id,
        payment_id=payment_id,
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def application_repository():
    repository = Mock()
    repository.get_by_id.return_value = make_application()
    return repository


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def use_case(
    application_repository,
    event_service,
):
    return CompleteRentalPaymentUseCase(
        application_repository=application_repository,
        event_service=event_service,
    )


@pytest.fixture
def dto():
    return make_dto()


# ============================================================
# APPLICATION NOT FOUND
# ============================================================


def test_application_not_found(
    use_case,
    application_repository,
    event_service,
    dto,
):
    application_repository.get_by_id.return_value = None

    with pytest.raises(ApplicationNotFound):
        use_case.execute(dto)

    application_repository.get_by_id.assert_called_once_with(
        dto.application_id
    )

    application_repository.update.assert_not_called()
    event_service.log.assert_not_called()


# ============================================================
# IDEMPOTENCE
# ============================================================


def test_completed_application_is_not_updated_again(
    use_case,
    application_repository,
    event_service,
    dto,
):
    application = make_application(
        status=ApplicationStatus.COMPLETED,
    )

    application_repository.get_by_id.return_value = application

    result = use_case.execute(dto)

    application_repository.update.assert_not_called()
    event_service.log.assert_not_called()

    assert isinstance(
        result,
        CompleteRentalPaymentResult,
    )

    assert result.application_id == application.id
    assert result.vehicle_id == application.vehicle.id
    assert result.rental_started is True
    assert result.message == "Location déjà activée"


def test_completed_application_returns_success(
    use_case,
    application_repository,
    dto,
):
    application = make_application(
        status=ApplicationStatus.COMPLETED,
    )

    application_repository.get_by_id.return_value = application

    result = use_case.execute(dto)

    assert result.rental_started is True
    assert result.application_id == "application-1"
    assert result.vehicle_id == "vehicle-1"


# ============================================================
# APPLICATION STATUS
# ============================================================


def test_application_status_becomes_completed(
    use_case,
    application_repository,
    dto,
):
    application = make_application(
        status=ApplicationStatus.APPROVED,
    )

    application_repository.get_by_id.return_value = application

    use_case.execute(dto)

    assert application.status == ApplicationStatus.COMPLETED


def test_application_is_updated(
    use_case,
    application_repository,
    dto,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    use_case.execute(dto)

    application_repository.update.assert_called_once_with(
        application
    )


# ============================================================
# VEHICLE
# ============================================================


def test_vehicle_is_retrieved_from_application(
    use_case,
    application_repository,
    dto,
):
    vehicle = make_vehicle(
        vehicle_id="vehicle-42"
    )

    application = make_application(
        vehicle=vehicle
    )

    application_repository.get_by_id.return_value = application

    result = use_case.execute(dto)

    assert result.vehicle_id == "vehicle-42"


# ============================================================
# EVENT
# ============================================================


def test_rental_payment_paid_event_is_logged(
    use_case,
    application_repository,
    event_service,
    dto,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    use_case.execute(dto)

    event_service.log.assert_called_once()

    event = event_service.log.call_args.kwargs

    assert event["type"] == EventType.RENTAL_PAYMENT_PAID
    assert event["application_id"] == application.id
    assert event["vehicle_id"] == application.vehicle.id
    assert event["user_id"] == application.user_id

    assert event["message"] == (
        "Paiement location confirmé"
    )


def test_event_contains_payment_id(
    use_case,
    application_repository,
    event_service,
    dto,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    use_case.execute(dto)

    event = event_service.log.call_args.kwargs

    assert event["event_metadata"]["payment_id"] == (
        dto.payment_id
    )


def test_event_contains_vehicle_id(
    use_case,
    application_repository,
    event_service,
    dto,
):
    application = make_application(
        vehicle=make_vehicle(
            vehicle_id="vehicle-99"
        )
    )

    application_repository.get_by_id.return_value = application

    use_case.execute(dto)

    event = event_service.log.call_args.kwargs

    assert event["event_metadata"]["vehicle_id"] == (
        "vehicle-99"
    )


# ============================================================
# RESULT
# ============================================================


def test_success_result_is_returned(
    use_case,
    application_repository,
    dto,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    result = use_case.execute(dto)

    assert isinstance(
        result,
        CompleteRentalPaymentResult,
    )


def test_success_result_contains_application_id(
    use_case,
    application_repository,
    dto,
):
    application = make_application(
        application_id="application-42"
    )

    application_repository.get_by_id.return_value = application

    result = use_case.execute(dto)

    assert result.application_id == "application-42"


def test_success_result_contains_vehicle_id(
    use_case,
    application_repository,
    dto,
):
    application = make_application(
        vehicle=make_vehicle(
            vehicle_id="vehicle-42"
        )
    )

    application_repository.get_by_id.return_value = application

    result = use_case.execute(dto)

    assert result.vehicle_id == "vehicle-42"


def test_success_result_indicates_rental_started(
    use_case,
    application_repository,
    dto,
):
    application_repository.get_by_id.return_value = (
        make_application()
    )

    result = use_case.execute(dto)

    assert result.rental_started is True


def test_success_result_message(
    use_case,
    application_repository,
    dto,
):
    application_repository.get_by_id.return_value = (
        make_application()
    )

    result = use_case.execute(dto)

    assert result.message == (
        "Location activée avec succès"
    )


# ============================================================
# COMPLETE FLOW
# ============================================================


def test_complete_payment_flow(
    use_case,
    application_repository,
    event_service,
):
    application = make_application(
        application_id="application-42",
        user_id="user-42",
        vehicle=make_vehicle(
            vehicle_id="vehicle-42"
        ),
    )

    dto = CompleteRentalPaymentDTO(
        application_id="application-42",
        payment_id="payment-1",
    )

    application_repository.get_by_id.return_value = application

    result = use_case.execute(dto)

    # Application
    application_repository.get_by_id.assert_called_once_with(
        "application-42"
    )

    application_repository.update.assert_called_once_with(
        application
    )

    # Event
    event_service.log.assert_called_once_with(
        type=EventType.RENTAL_PAYMENT_PAID,
        application_id="application-42",
        vehicle_id="vehicle-42",
        user_id="user-42",
        message="Paiement location confirmé",
        event_metadata={
            "payment_id": "payment-1",
            "vehicle_id": "vehicle-42",
        },
    )

    # Result
    assert result.application_id == "application-42"
    assert result.vehicle_id == "vehicle-42"
    assert result.rental_started is True
    assert result.message == "Location activée avec succès"

# ============================================================
# ERRORS / RAISE
# ============================================================


def test_application_repository_error_is_propagated(
    use_case,
    application_repository,
    event_service,
    dto,
):
    application_repository.get_by_id.side_effect = (
        RuntimeError("repository error")
    )

    with pytest.raises(
        RuntimeError,
        match="repository error",
    ):
        use_case.execute(dto)

    event_service.log.assert_not_called()


def test_update_error_is_propagated(
    use_case,
    application_repository,
    event_service,
    dto,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    application_repository.update.side_effect = (
        RuntimeError("update error")
    )

    with pytest.raises(
        RuntimeError,
        match="update error",
    ):
        use_case.execute(dto)

    event_service.log.assert_not_called()


def test_event_error_is_propagated(
    use_case,
    application_repository,
    event_service,
    dto,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    event_service.log.side_effect = (
        RuntimeError("event error")
    )

    with pytest.raises(
        RuntimeError,
        match="event error",
    ):
        use_case.execute(dto)