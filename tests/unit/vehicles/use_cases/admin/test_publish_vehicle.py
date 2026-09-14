from unittest.mock import Mock

import pytest

from modules.vehicles.application.dtos.admin.vehicle_admin_action_dto import (
    VehicleAdminActionDTO,
)
from modules.vehicles.application.results.admin.publish_vehicle_result import (
    PublishVehicleResult,
)
from modules.vehicles.application.use_cases.admin.publish_vehicle import (
    PublishVehicleUseCase,
)

from modules.vehicles.domain.enums import VehicleStatus
from modules.vehicles.domain.exceptions import (
    VehicleAlreadyPublished,
    VehicleNotFound,
    VehicleNotReadyForPublication,
)

from modules.applications.domain.enums import EventType


# ============================================================
# HELPERS
# ============================================================


def make_dto(
    *,
    vehicle_id="vehicle-1",
    admin_id="admin-1",
):
    return VehicleAdminActionDTO(
        vehicle_id=vehicle_id,
        admin_id=admin_id,
    )


def make_vehicle(
    *,
    vehicle_id="vehicle-1",
    status=VehicleStatus.READY,
):
    vehicle = Mock(
        id=vehicle_id,
        status=status,
    )

    # Simulate the domain transition.
    def publish():
        vehicle.status = VehicleStatus.PUBLISHED

    vehicle.publish.side_effect = publish

    return vehicle


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def vehicle_repository():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def uow():
    return Mock()


@pytest.fixture
def use_case(
    vehicle_repository,
    event_service,
    uow,
):
    return PublishVehicleUseCase(
        vehicle_repository=vehicle_repository,
        event_service=event_service,
        unit_of_work=uow,
    )


# ============================================================
# SUCCESS
# ============================================================


def test_publish_vehicle_success(
    use_case,
    vehicle_repository,
    event_service,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle_repository.get_by_id.return_value = vehicle

    result = use_case.execute(dto)

    assert isinstance(
        result,
        PublishVehicleResult,
    )

    assert result.vehicle_id == "vehicle-1"

    assert result.status == (
        VehicleStatus.PUBLISHED.value
    )

    assert result.message == "Véhicule publié"

    vehicle.publish.assert_called_once()

    vehicle_repository.update.assert_called_once_with(
        vehicle
    )

    event_service.log.assert_called_once()

    uow.commit.assert_called_once()

    uow.rollback.assert_not_called()


# ============================================================
# VEHICLE NOT FOUND
# ============================================================


def test_vehicle_not_found(
    use_case,
    vehicle_repository,
    event_service,
    uow,
):
    dto = make_dto()

    vehicle_repository.get_by_id.return_value = None

    with pytest.raises(VehicleNotFound):
        use_case.execute(dto)

    vehicle_repository.get_by_id.assert_called_once_with(
        "vehicle-1"
    )

    vehicle_repository.update.assert_not_called()

    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


# ============================================================
# ALREADY PUBLISHED
# ============================================================


def test_already_published_vehicle_cannot_be_published(
    use_case,
    vehicle_repository,
    event_service,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle(
        status=VehicleStatus.PUBLISHED,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    with pytest.raises(VehicleAlreadyPublished):
        use_case.execute(dto)

    vehicle.publish.assert_not_called()

    vehicle_repository.update.assert_not_called()

    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


# ============================================================
# VEHICLE NOT READY
# ============================================================


def test_vehicle_must_be_ready_before_publication(
    use_case,
    vehicle_repository,
    event_service,
    uow,
):
    dto = make_dto()

    non_ready_status = next(
        status
        for status in VehicleStatus
        if status not in (
            VehicleStatus.READY,
            VehicleStatus.PUBLISHED,
        )
    )

    vehicle = make_vehicle(
        status=non_ready_status,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    with pytest.raises(VehicleNotReadyForPublication):
        use_case.execute(dto)

    vehicle.publish.assert_not_called()

    vehicle_repository.update.assert_not_called()

    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


# ============================================================
# DOMAIN TRANSITION
# ============================================================


def test_vehicle_publish_method_is_called(
    use_case,
    vehicle_repository,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle_repository.get_by_id.return_value = vehicle

    use_case.execute(dto)

    vehicle.publish.assert_called_once()


def test_vehicle_status_becomes_published(
    use_case,
    vehicle_repository,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle_repository.get_by_id.return_value = vehicle

    use_case.execute(dto)

    assert vehicle.status == VehicleStatus.PUBLISHED


# ============================================================
# PERSISTENCE
# ============================================================


def test_vehicle_is_updated(
    use_case,
    vehicle_repository,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle_repository.get_by_id.return_value = vehicle

    use_case.execute(dto)

    vehicle_repository.update.assert_called_once_with(
        vehicle
    )


# ============================================================
# EVENT
# ============================================================


def test_vehicle_published_event_is_logged(
    use_case,
    vehicle_repository,
    event_service,
):
    dto = make_dto(
        admin_id="admin-42",
    )

    vehicle = make_vehicle(
        vehicle_id="vehicle-123",
    )

    vehicle_repository.get_by_id.return_value = vehicle

    use_case.execute(dto)

    event_service.log.assert_called_once()

    call_kwargs = event_service.log.call_args.kwargs

    assert call_kwargs["type"] == (
        EventType.VEHICLE_PUBLISHED
    )

    assert call_kwargs["message"] == (
        "Véhicule publié"
    )

    assert call_kwargs["vehicle_id"] == (
        "vehicle-123"
    )

    assert call_kwargs["user_id"] == (
        "admin-42"
    )

    assert call_kwargs["event_metadata"] == {
        "status": VehicleStatus.PUBLISHED.value,
    }


# ============================================================
# COMMIT
# ============================================================


def test_commit_is_called(
    use_case,
    vehicle_repository,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle_repository.get_by_id.return_value = vehicle

    use_case.execute(dto)

    uow.commit.assert_called_once()

    uow.rollback.assert_not_called()


def test_commit_happens_after_update_and_event(
    use_case,
    vehicle_repository,
    event_service,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle_repository.get_by_id.return_value = vehicle

    call_order = []

    vehicle_repository.update.side_effect = (
        lambda vehicle: call_order.append("update")
    )

    event_service.log.side_effect = (
        lambda **kwargs: call_order.append("event")
    )

    uow.commit.side_effect = (
        lambda: call_order.append("commit")
    )

    use_case.execute(dto)

    assert call_order == [
        "update",
        "event",
        "commit",
    ]


# ============================================================
# RESULT
# ============================================================


def test_publish_result_contains_expected_values(
    use_case,
    vehicle_repository,
):
    dto = make_dto()

    vehicle = make_vehicle(
        vehicle_id="vehicle-99",
    )

    vehicle_repository.get_by_id.return_value = vehicle

    result = use_case.execute(dto)

    assert isinstance(
        result,
        PublishVehicleResult,
    )

    assert result.vehicle_id == "vehicle-99"

    assert result.status == (
        VehicleStatus.PUBLISHED.value
    )

    assert result.message == "Véhicule publié"


# ============================================================
# REPOSITORY ERROR
# ============================================================


def test_get_vehicle_error_rolls_back(
    use_case,
    vehicle_repository,
    uow,
):
    dto = make_dto()

    vehicle_repository.get_by_id.side_effect = RuntimeError(
        "repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="repository error",
    ):
        use_case.execute(dto)

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_update_error_rolls_back(
    use_case,
    vehicle_repository,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle_repository.get_by_id.return_value = vehicle

    vehicle_repository.update.side_effect = RuntimeError(
        "update error"
    )

    with pytest.raises(
        RuntimeError,
        match="update error",
    ):
        use_case.execute(dto)

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


# ============================================================
# EVENT ERROR
# ============================================================


def test_event_error_rolls_back(
    use_case,
    vehicle_repository,
    event_service,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle_repository.get_by_id.return_value = vehicle

    event_service.log.side_effect = RuntimeError(
        "event error"
    )

    with pytest.raises(
        RuntimeError,
        match="event error",
    ):
        use_case.execute(dto)

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


# ============================================================
# COMMIT ERROR
# ============================================================


def test_commit_error_rolls_back(
    use_case,
    vehicle_repository,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle_repository.get_by_id.return_value = vehicle

    uow.commit.side_effect = RuntimeError(
        "commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="commit error",
    ):
        use_case.execute(dto)

    uow.commit.assert_called_once()

    uow.rollback.assert_called_once()


# ============================================================
# VALIDATION BEFORE MODIFICATION
# ============================================================


@pytest.mark.parametrize(
    "status, expected_exception",
    [
        (
            VehicleStatus.PUBLISHED,
            VehicleAlreadyPublished,
        ),
    ],
)
def test_invalid_status_does_not_modify_vehicle(
    status,
    expected_exception,
    use_case,
    vehicle_repository,
    event_service,
):
    dto = make_dto()

    vehicle = make_vehicle(
        status=status,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    with pytest.raises(expected_exception):
        use_case.execute(dto)

    vehicle.publish.assert_not_called()

    vehicle_repository.update.assert_not_called()

    event_service.log.assert_not_called()


# ============================================================
# EXACT VEHICLE ID
# ============================================================


@pytest.mark.parametrize(
    "vehicle_id",
    [
        "vehicle-1",
        "vehicle-42",
        "vehicle-99",
        "550e8400-e29b-41d4-a716-446655440000",
    ],
)
def test_execute_uses_exact_vehicle_id(
    vehicle_id,
    use_case,
    vehicle_repository,
):
    dto = make_dto(
        vehicle_id=vehicle_id,
    )

    vehicle = make_vehicle(
        vehicle_id=vehicle_id,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    result = use_case.execute(dto)

    vehicle_repository.get_by_id.assert_called_once_with(
        vehicle_id
    )

    assert result.vehicle_id == vehicle_id