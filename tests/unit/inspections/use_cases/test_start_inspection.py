from unittest.mock import Mock

import pytest

from modules.inspections.application.results.start_inspection_result import (
    StartInspectionResult,
)
from modules.inspections.application.use_cases.admin.start_inspection import (
    StartInspectionUseCase,
)
from modules.inspections.domain.entities.inspection import Inspection
from modules.vehicles.domain.exceptions import VehicleNotFound


@pytest.fixture
def vehicle_repository():
    return Mock()


@pytest.fixture
def inspection_repository():
    return Mock()


@pytest.fixture
def job_queue():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    vehicle_repository,
    inspection_repository,
    job_queue,
    unit_of_work,
):
    return StartInspectionUseCase(
        vehicle_repository=vehicle_repository,
        inspection_repository=inspection_repository,
        job_queue=job_queue,
        unit_of_work=unit_of_work,
    )


@pytest.fixture
def vehicle():
    vehicle = Mock()
    vehicle.id = "vehicle-123"
    return vehicle


def test_execute_creates_inspection_and_queues_job(
    use_case,
    vehicle_repository,
    inspection_repository,
    job_queue,
    unit_of_work,
    vehicle,
):
    vehicle_repository.get_by_id.return_value = vehicle

    result = use_case.execute(
        vehicle_id="vehicle-123",
        admin_id="admin-123",
    )

    assert isinstance(result, StartInspectionResult)
    assert result.vehicle_id == "vehicle-123"
    assert result.status == "QUEUED"
    assert result.message == "Inspection mise en file d'attente"
    assert result.inspection_id

    vehicle_repository.get_by_id.assert_called_once_with(
        "vehicle-123"
    )

    inspection_repository.save.assert_called_once()

    inspection = inspection_repository.save.call_args.args[0]

    assert isinstance(inspection, Inspection)
    assert inspection.id == result.inspection_id
    assert inspection.vehicle_id == "vehicle-123"

    vehicle.ensure_can_be_inspected.assert_called_once_with()
    vehicle.request_inspection.assert_called_once_with()

    vehicle_repository.update.assert_called_once_with(
        vehicle
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()

    job_queue.enqueue_inspection.assert_called_once_with(
        "vehicle-123",
        "admin-123",
    )


def test_execute_raises_when_vehicle_not_found(
    use_case,
    vehicle_repository,
    inspection_repository,
    job_queue,
    unit_of_work,
):
    vehicle_repository.get_by_id.return_value = None

    with pytest.raises(VehicleNotFound):
        use_case.execute(
            vehicle_id="vehicle-123",
            admin_id="admin-123",
        )

    inspection_repository.save.assert_not_called()
    vehicle_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()

    job_queue.enqueue_inspection.assert_not_called()


def test_execute_rolls_back_when_vehicle_cannot_be_inspected(
    use_case,
    vehicle_repository,
    inspection_repository,
    unit_of_work,
    job_queue,
    vehicle,
):
    vehicle_repository.get_by_id.return_value = vehicle

    vehicle.ensure_can_be_inspected.side_effect = RuntimeError(
        "Vehicle cannot be inspected"
    )

    with pytest.raises(
        RuntimeError,
        match="Vehicle cannot be inspected",
    ):
        use_case.execute(
            vehicle_id="vehicle-123",
            admin_id="admin-123",
        )

    inspection_repository.save.assert_not_called()
    vehicle_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()

    job_queue.enqueue_inspection.assert_not_called()


def test_execute_rolls_back_when_inspection_save_fails(
    use_case,
    vehicle_repository,
    inspection_repository,
    unit_of_work,
    job_queue,
    vehicle,
):
    vehicle_repository.get_by_id.return_value = vehicle

    inspection_repository.save.side_effect = RuntimeError(
        "Save error"
    )

    with pytest.raises(
        RuntimeError,
        match="Save error",
    ):
        use_case.execute(
            vehicle_id="vehicle-123",
            admin_id="admin-123",
        )

    vehicle.ensure_can_be_inspected.assert_called_once_with()
    vehicle.request_inspection.assert_not_called()
    vehicle_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()

    job_queue.enqueue_inspection.assert_not_called()


def test_execute_rolls_back_when_vehicle_update_fails(
    use_case,
    vehicle_repository,
    inspection_repository,
    unit_of_work,
    job_queue,
    vehicle,
):
    vehicle_repository.get_by_id.return_value = vehicle

    vehicle_repository.update.side_effect = RuntimeError(
        "Update error"
    )

    with pytest.raises(
        RuntimeError,
        match="Update error",
    ):
        use_case.execute(
            vehicle_id="vehicle-123",
            admin_id="admin-123",
        )

    inspection_repository.save.assert_called_once()

    vehicle.request_inspection.assert_called_once_with()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()

    job_queue.enqueue_inspection.assert_not_called()


def test_execute_rolls_back_when_commit_fails(
    use_case,
    vehicle_repository,
    inspection_repository,
    unit_of_work,
    job_queue,
    vehicle,
):
    vehicle_repository.get_by_id.return_value = vehicle

    unit_of_work.commit.side_effect = RuntimeError(
        "Commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="Commit error",
    ):
        use_case.execute(
            vehicle_id="vehicle-123",
            admin_id="admin-123",
        )

    inspection_repository.save.assert_called_once()
    vehicle_repository.update.assert_called_once_with(
        vehicle
    )

    unit_of_work.rollback.assert_called_once()

    job_queue.enqueue_inspection.assert_not_called()


def test_execute_does_not_rollback_when_queue_fails(
    use_case,
    vehicle_repository,
    inspection_repository,
    unit_of_work,
    job_queue,
    vehicle,
):
    vehicle_repository.get_by_id.return_value = vehicle

    job_queue.enqueue_inspection.side_effect = RuntimeError(
        "Queue error"
    )

    with pytest.raises(
        RuntimeError,
        match="Queue error",
    ):
        use_case.execute(
            vehicle_id="vehicle-123",
            admin_id="admin-123",
        )

    # La transaction DB a déjà été validée.
    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()

    inspection_repository.save.assert_called_once()
    vehicle_repository.update.assert_called_once_with(
        vehicle
    )

    job_queue.enqueue_inspection.assert_called_once_with(
        "vehicle-123",
        "admin-123",
    )