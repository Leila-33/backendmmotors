from unittest.mock import Mock

import pytest

from modules.vehicles.application.dtos.admin.vehicle_admin_action_dto import (
    VehicleAdminActionDTO,
)
from modules.vehicles.application.results.admin.final_check_result import (
    FinalCheckResult,
)
from modules.vehicles.application.use_cases.admin.final_check import (
    FinalCheckUseCase,
)

from modules.vehicles.domain.exceptions import (
    VehicleNotFound,
    VehicleNotReadyForFinalCheck,
)

from modules.reconditionings.domain.exceptions import (
    ReconditioningNotFound,
    ReconditioningNotCompleted,
)

from modules.reconditionings.domain.enums import (
    ReconditioningStatus,
)

from modules.vehicles.domain.enums import (
    VehicleStatus,
)

from modules.applications.domain.enums import (
    EventType,
)


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
    status=VehicleStatus.RECONDITIONED,
):
    vehicle = Mock(
        id=vehicle_id,
        status=status,
        final_check_at=None,
    )

    # Simulate the domain transition.
    def mark_as_ready():
        vehicle.status = VehicleStatus.AVAILABLE

    vehicle.mark_as_ready.side_effect = mark_as_ready

    return vehicle


def make_reconditioning(
    *,
    status=ReconditioningStatus.COMPLETED,
):
    reconditioning = Mock(
        status=status,
    )

    # The real domain method should move the
    # reconditioning to its approved/completed state.
    reconditioning.approve = Mock()

    return reconditioning


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def vehicle_repository():
    return Mock()


@pytest.fixture
def reconditioning_repository():
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
    reconditioning_repository,
    event_service,
    uow,
):
    return FinalCheckUseCase(
        vehicle_repository=vehicle_repository,
        reconditioning_repository=reconditioning_repository,
        event_service=event_service,
        unit_of_work=uow,
    )


# ============================================================
# SUCCESS
# ============================================================


def test_final_check_success(
    use_case,
    vehicle_repository,
    reconditioning_repository,
    event_service,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    reconditioning = make_reconditioning()

    vehicle_repository.get_by_id.return_value = vehicle

    reconditioning_repository.get_by_vehicle_id.return_value = (
        reconditioning
    )

    result = use_case.execute(dto)

    assert isinstance(
        result,
        FinalCheckResult,
    )

    assert result.vehicle_id == "vehicle-1"

    assert result.vehicle_status == (
        VehicleStatus.AVAILABLE.value
    )

    assert result.reconditioning_status == (
        ReconditioningStatus.COMPLETED.value
    )

    assert result.final_check_at is not None

    assert result.final_check_at.tzinfo is not None

    reconditioning.approve.assert_called_once()

    vehicle.mark_as_ready.assert_called_once()

    reconditioning_repository.update.assert_called_once_with(
        reconditioning
    )

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
    reconditioning_repository,
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

    reconditioning_repository.get_by_vehicle_id.assert_not_called()

    reconditioning_repository.update.assert_not_called()

    vehicle_repository.update.assert_not_called()

    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


# ============================================================
# RECONDITIONING NOT FOUND
# ============================================================


def test_reconditioning_not_found(
    use_case,
    vehicle_repository,
    reconditioning_repository,
    event_service,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle_repository.get_by_id.return_value = vehicle

    reconditioning_repository.get_by_vehicle_id.return_value = None

    with pytest.raises(ReconditioningNotFound):
        use_case.execute(dto)

    vehicle_repository.get_by_id.assert_called_once_with(
        "vehicle-1"
    )

    reconditioning_repository.get_by_vehicle_id.assert_called_once_with(
        "vehicle-1"
    )

    reconditioning_repository.update.assert_not_called()

    vehicle_repository.update.assert_not_called()

    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


# ============================================================
# RECONDITIONING NOT COMPLETED
# ============================================================


def test_reconditioning_must_be_completed(
    use_case,
    vehicle_repository,
    reconditioning_repository,
    event_service,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    reconditioning = make_reconditioning(
        status=next(
            status
            for status in ReconditioningStatus
            if status != ReconditioningStatus.COMPLETED
        )
    )

    vehicle_repository.get_by_id.return_value = vehicle

    reconditioning_repository.get_by_vehicle_id.return_value = (
        reconditioning
    )

    with pytest.raises(ReconditioningNotCompleted):
        use_case.execute(dto)

    reconditioning.approve.assert_not_called()

    vehicle.mark_as_ready.assert_not_called()

    reconditioning_repository.update.assert_not_called()

    vehicle_repository.update.assert_not_called()

    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


# ============================================================
# VEHICLE NOT READY
# ============================================================


def test_vehicle_must_be_reconditioned_before_final_check(
    use_case,
    vehicle_repository,
    reconditioning_repository,
    event_service,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle(
        status=next(
            status
            for status in VehicleStatus
            if status != VehicleStatus.RECONDITIONED
        )
    )

    reconditioning = make_reconditioning()

    vehicle_repository.get_by_id.return_value = vehicle

    reconditioning_repository.get_by_vehicle_id.return_value = (
        reconditioning
    )

    with pytest.raises(VehicleNotReadyForFinalCheck):
        use_case.execute(dto)

    reconditioning.approve.assert_not_called()

    vehicle.mark_as_ready.assert_not_called()

    reconditioning_repository.update.assert_not_called()

    vehicle_repository.update.assert_not_called()

    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


# ============================================================
# EXACT REPOSITORY CALLS
# ============================================================


def test_vehicle_is_loaded_with_exact_id(
    use_case,
    vehicle_repository,
    reconditioning_repository,
):
    dto = make_dto(
        vehicle_id="vehicle-42",
    )

    vehicle = make_vehicle(
        vehicle_id="vehicle-42",
    )

    reconditioning = make_reconditioning()

    vehicle_repository.get_by_id.return_value = vehicle

    reconditioning_repository.get_by_vehicle_id.return_value = (
        reconditioning
    )

    use_case.execute(dto)

    vehicle_repository.get_by_id.assert_called_once_with(
        "vehicle-42"
    )

    reconditioning_repository.get_by_vehicle_id.assert_called_once_with(
        "vehicle-42"
    )


# ============================================================
# DOMAIN TRANSITIONS
# ============================================================


def test_reconditioning_is_approved(
    use_case,
    vehicle_repository,
    reconditioning_repository,
):
    dto = make_dto()

    vehicle = make_vehicle()

    reconditioning = make_reconditioning()

    vehicle_repository.get_by_id.return_value = vehicle

    reconditioning_repository.get_by_vehicle_id.return_value = (
        reconditioning
    )

    use_case.execute(dto)

    reconditioning.approve.assert_called_once()


def test_vehicle_is_marked_as_ready(
    use_case,
    vehicle_repository,
    reconditioning_repository,
):
    dto = make_dto()

    vehicle = make_vehicle()

    reconditioning = make_reconditioning()

    vehicle_repository.get_by_id.return_value = vehicle

    reconditioning_repository.get_by_vehicle_id.return_value = (
        reconditioning
    )

    use_case.execute(dto)

    vehicle.mark_as_ready.assert_called_once()

    assert vehicle.status == VehicleStatus.AVAILABLE


# ============================================================
# FINAL CHECK DATE
# ============================================================


def test_final_check_date_is_set(
    use_case,
    vehicle_repository,
    reconditioning_repository,
):
    dto = make_dto()

    vehicle = make_vehicle()

    reconditioning = make_reconditioning()

    vehicle_repository.get_by_id.return_value = vehicle

    reconditioning_repository.get_by_vehicle_id.return_value = (
        reconditioning
    )

    assert vehicle.final_check_at is None

    use_case.execute(dto)

    assert vehicle.final_check_at is not None

    assert vehicle.final_check_at.tzinfo is not None

    assert (
        vehicle.final_check_at.utcoffset()
        is not None
    )


# ============================================================
# PERSISTENCE
# ============================================================


def test_reconditioning_is_updated(
    use_case,
    vehicle_repository,
    reconditioning_repository,
):
    dto = make_dto()

    vehicle = make_vehicle()

    reconditioning = make_reconditioning()

    vehicle_repository.get_by_id.return_value = vehicle

    reconditioning_repository.get_by_vehicle_id.return_value = (
        reconditioning
    )

    use_case.execute(dto)

    reconditioning_repository.update.assert_called_once_with(
        reconditioning
    )


def test_vehicle_is_updated(
    use_case,
    vehicle_repository,
    reconditioning_repository,
):
    dto = make_dto()

    vehicle = make_vehicle()

    reconditioning = make_reconditioning()

    vehicle_repository.get_by_id.return_value = vehicle

    reconditioning_repository.get_by_vehicle_id.return_value = (
        reconditioning
    )

    use_case.execute(dto)

    vehicle_repository.update.assert_called_once_with(
        vehicle
    )


# ============================================================
# EVENT
# ============================================================


def test_final_check_event_is_logged(
    use_case,
    vehicle_repository,
    reconditioning_repository,
    event_service,
):
    dto = make_dto(
        admin_id="admin-42",
    )

    vehicle = make_vehicle(
        vehicle_id="vehicle-123",
    )

    reconditioning = make_reconditioning()

    vehicle_repository.get_by_id.return_value = vehicle

    reconditioning_repository.get_by_vehicle_id.return_value = (
        reconditioning
    )

    use_case.execute(dto)

    event_service.log.assert_called_once()

    call_kwargs = event_service.log.call_args.kwargs

    assert call_kwargs["type"] == (
        EventType.FINAL_CHECK_COMPLETED
    )

    assert call_kwargs["message"] == (
        "Contrôle final terminé"
    )

    assert call_kwargs["vehicle_id"] == "vehicle-123"

    assert call_kwargs["user_id"] == "admin-42"

    assert "final_check_at" in (
        call_kwargs["event_metadata"]
    )

    assert (
        call_kwargs["event_metadata"]["final_check_at"]
        == vehicle.final_check_at.isoformat()
    )


# ============================================================
# COMMIT
# ============================================================


def test_commit_is_called_after_persistence_and_event(
    use_case,
    vehicle_repository,
    reconditioning_repository,
    event_service,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    reconditioning = make_reconditioning()

    vehicle_repository.get_by_id.return_value = vehicle

    reconditioning_repository.get_by_vehicle_id.return_value = (
        reconditioning
    )

    call_order = []

    reconditioning_repository.update.side_effect = (
        lambda obj: call_order.append(
            "reconditioning_update"
        )
    )

    vehicle_repository.update.side_effect = (
        lambda obj: call_order.append(
            "vehicle_update"
        )
    )

    event_service.log.side_effect = (
        lambda **kwargs: call_order.append(
            "event"
        )
    )

    uow.commit.side_effect = (
        lambda: call_order.append(
            "commit"
        )
    )

    use_case.execute(dto)

    assert call_order == [
        "reconditioning_update",
        "vehicle_update",
        "event",
        "commit",
    ]


# ============================================================
# ROLLBACK — REPOSITORIES
# ============================================================


def test_reconditioning_update_error_rolls_back(
    use_case,
    vehicle_repository,
    reconditioning_repository,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    reconditioning = make_reconditioning()

    vehicle_repository.get_by_id.return_value = vehicle

    reconditioning_repository.get_by_vehicle_id.return_value = (
        reconditioning
    )

    reconditioning_repository.update.side_effect = RuntimeError(
        "reconditioning update error"
    )

    with pytest.raises(
        RuntimeError,
        match="reconditioning update error",
    ):
        use_case.execute(dto)

    vehicle_repository.update.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_vehicle_update_error_rolls_back(
    use_case,
    vehicle_repository,
    reconditioning_repository,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    reconditioning = make_reconditioning()

    vehicle_repository.get_by_id.return_value = vehicle

    reconditioning_repository.get_by_vehicle_id.return_value = (
        reconditioning
    )

    vehicle_repository.update.side_effect = RuntimeError(
        "vehicle update error"
    )

    with pytest.raises(
        RuntimeError,
        match="vehicle update error",
    ):
        use_case.execute(dto)

    event_service = use_case.event_service

    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


# ============================================================
# ROLLBACK — EVENT
# ============================================================


def test_event_error_rolls_back(
    use_case,
    vehicle_repository,
    reconditioning_repository,
    event_service,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    reconditioning = make_reconditioning()

    vehicle_repository.get_by_id.return_value = vehicle

    reconditioning_repository.get_by_vehicle_id.return_value = (
        reconditioning
    )

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
# ROLLBACK — COMMIT
# ============================================================


def test_commit_error_rolls_back(
    use_case,
    vehicle_repository,
    reconditioning_repository,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    reconditioning = make_reconditioning()

    vehicle_repository.get_by_id.return_value = vehicle

    reconditioning_repository.get_by_vehicle_id.return_value = (
        reconditioning
    )

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
# REPOSITORY ERRORS
# ============================================================


def test_vehicle_repository_error_is_propagated(
    use_case,
    vehicle_repository,
    uow,
):
    dto = make_dto()

    vehicle_repository.get_by_id.side_effect = RuntimeError(
        "vehicle repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="vehicle repository error",
    ):
        use_case.execute(dto)

    uow.rollback.assert_called_once()

    uow.commit.assert_not_called()


def test_reconditioning_repository_error_is_propagated(
    use_case,
    vehicle_repository,
    reconditioning_repository,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle_repository.get_by_id.return_value = vehicle

    reconditioning_repository.get_by_vehicle_id.side_effect = (
        RuntimeError(
            "reconditioning repository error"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="reconditioning repository error",
    ):
        use_case.execute(dto)

    uow.rollback.assert_called_once()

    uow.commit.assert_not_called()


# ============================================================
# NO UNEXPECTED ACTIONS AFTER VALIDATION FAILURE
# ============================================================


def test_reconditioning_validation_happens_before_updates(
    use_case,
    vehicle_repository,
    reconditioning_repository,
):
    dto = make_dto()

    vehicle = make_vehicle()

    reconditioning = make_reconditioning(
        status=next(
            status
            for status in ReconditioningStatus
            if status != ReconditioningStatus.COMPLETED
        )
    )

    vehicle_repository.get_by_id.return_value = vehicle

    reconditioning_repository.get_by_vehicle_id.return_value = (
        reconditioning
    )

    with pytest.raises(ReconditioningNotCompleted):
        use_case.execute(dto)

    reconditioning_repository.update.assert_not_called()

    vehicle_repository.update.assert_not_called()


def test_vehicle_state_validation_happens_before_updates(
    use_case,
    vehicle_repository,
    reconditioning_repository,
):
    dto = make_dto()

    vehicle = make_vehicle(
        status=next(
            status
            for status in VehicleStatus
            if status != VehicleStatus.RECONDITIONED
        )
    )

    reconditioning = make_reconditioning()

    vehicle_repository.get_by_id.return_value = vehicle

    reconditioning_repository.get_by_vehicle_id.return_value = (
        reconditioning
    )

    with pytest.raises(VehicleNotReadyForFinalCheck):
        use_case.execute(dto)

    reconditioning.approve.assert_not_called()

    vehicle.mark_as_ready.assert_not_called()

    reconditioning_repository.update.assert_not_called()

    vehicle_repository.update.assert_not_called()


# ============================================================
# DIFFERENT VEHICLE ID
# ============================================================


def test_execute_uses_dto_vehicle_id(
    use_case,
    vehicle_repository,
    reconditioning_repository,
):
    dto = make_dto(
        vehicle_id="vehicle-99",
    )

    vehicle = make_vehicle(
        vehicle_id="vehicle-99",
    )

    reconditioning = make_reconditioning()

    vehicle_repository.get_by_id.return_value = vehicle

    reconditioning_repository.get_by_vehicle_id.return_value = (
        reconditioning
    )

    result = use_case.execute(dto)

    assert result.vehicle_id == "vehicle-99"

    vehicle_repository.get_by_id.assert_called_once_with(
        "vehicle-99"
    )

    reconditioning_repository.get_by_vehicle_id.assert_called_once_with(
        "vehicle-99"
    )