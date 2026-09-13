from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from modules.inspections.domain.enums import InspectionStatus
from modules.inspections.domain.exceptions import (
    InspectionNotCompleted,
    InspectionNotFound,
)
from modules.reconditionings.domain.enums import ReconditioningStatus
from modules.reconditionings.domain.exceptions import (
    ReconditioningAlreadyRunning,
)
from modules.reconditionings.application.dtos.admin.start_reconditioning_dto import (
    StartReconditioningDTO,
)
from modules.reconditionings.application.results.admin.start_reconditioning_result import (
    StartReconditioningResult,
)
from modules.reconditionings.application.use_cases.admin.start_reconditioning import (
    StartReconditioningUseCase,
)
from modules.vehicles.domain.enums import VehicleStatus
from modules.vehicles.domain.exceptions import (
    VehicleNotEligibleForReconditioning,
    VehicleNotFound,
)


@pytest.fixture
def reconditioning_repository():
    return Mock()


@pytest.fixture
def inspection_repository():
    return Mock()


@pytest.fixture
def vehicle_repository():
    return Mock()


@pytest.fixture
def job_queue():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    reconditioning_repository,
    inspection_repository,
    vehicle_repository,
    job_queue,
    unit_of_work,
):
    return StartReconditioningUseCase(
        reconditioning_repository=reconditioning_repository,
        inspection_repository=inspection_repository,
        vehicle_repository=vehicle_repository,
        job_queue=job_queue,
        unit_of_work=unit_of_work,
    )


@pytest.fixture
def dto():
    return StartReconditioningDTO(
        vehicle_id="vehicle-123",
        admin_id="admin-123",
    )


@pytest.fixture
def vehicle():
    vehicle = Mock()
    vehicle.id = "vehicle-123"
    vehicle.status = VehicleStatus.INSPECTED
    return vehicle


@pytest.fixture
def inspection():
    inspection = Mock()
    inspection.status = InspectionStatus.COMPLETED
    return inspection


def configure_success(
    vehicle_repository,
    inspection_repository,
    reconditioning_repository,
    vehicle,
    inspection,
):
    vehicle_repository.get_by_id.return_value = vehicle
    inspection_repository.get_by_vehicle_id.return_value = inspection
    reconditioning_repository.get_by_vehicle_id.return_value = None


def test_execute_starts_reconditioning_successfully(
    use_case,
    vehicle_repository,
    inspection_repository,
    reconditioning_repository,
    job_queue,
    unit_of_work,
    dto,
    vehicle,
    inspection,
):
    configure_success(
        vehicle_repository,
        inspection_repository,
        reconditioning_repository,
        vehicle,
        inspection,
    )

    reconditioning = SimpleNamespace(
        id="reconditioning-123",
        vehicle_id="vehicle-123",
        status=ReconditioningStatus.PENDING,
    )

    with patch(
        "modules.reconditionings.application.use_cases.admin.start_reconditioning.Reconditioning.create",
        return_value=reconditioning,
    ):
        result = use_case.execute(dto)

    assert isinstance(result, StartReconditioningResult)
    assert result.reconditioning_id == "reconditioning-123"
    assert result.vehicle_id == "vehicle-123"
    assert result.status == ReconditioningStatus.PENDING.value
    assert result.message == "Reconditionnement lancé"

    vehicle_repository.get_by_id.assert_called_once_with(
        "vehicle-123"
    )
    inspection_repository.get_by_vehicle_id.assert_called_once_with(
        "vehicle-123"
    )
    reconditioning_repository.get_by_vehicle_id.assert_called_once_with(
        "vehicle-123"
    )

    vehicle.start_reconditioning.assert_called_once()

    reconditioning_repository.save.assert_called_once_with(
        reconditioning
    )
    vehicle_repository.update.assert_called_once_with(
        vehicle
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()

    job_queue.enqueue_reconditioning.assert_called_once_with(
        "reconditioning-123",
        "admin-123",
    )


def test_execute_raises_when_vehicle_does_not_exist(
    use_case,
    vehicle_repository,
    inspection_repository,
    reconditioning_repository,
    job_queue,
    unit_of_work,
    dto,
):
    vehicle_repository.get_by_id.return_value = None

    with pytest.raises(VehicleNotFound):
        use_case.execute(dto)

    vehicle_repository.get_by_id.assert_called_once_with(
        "vehicle-123"
    )

    inspection_repository.get_by_vehicle_id.assert_not_called()
    reconditioning_repository.get_by_vehicle_id.assert_not_called()
    reconditioning_repository.save.assert_not_called()
    vehicle_repository.update.assert_not_called()
    job_queue.enqueue_reconditioning.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_execute_raises_when_vehicle_is_already_in_reconditioning(
    use_case,
    vehicle_repository,
    inspection_repository,
    reconditioning_repository,
    job_queue,
    unit_of_work,
    dto,
    vehicle,
):
    vehicle.status = VehicleStatus.RECONDITIONING
    vehicle_repository.get_by_id.return_value = vehicle

    with pytest.raises(ReconditioningAlreadyRunning):
        use_case.execute(dto)

    vehicle_repository.get_by_id.assert_called_once_with(
        "vehicle-123"
    )

    inspection_repository.get_by_vehicle_id.assert_not_called()
    reconditioning_repository.get_by_vehicle_id.assert_not_called()
    reconditioning_repository.save.assert_not_called()
    vehicle_repository.update.assert_not_called()
    job_queue.enqueue_reconditioning.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_execute_raises_when_vehicle_is_not_inspected(
    use_case,
    vehicle_repository,
    inspection_repository,
    reconditioning_repository,
    job_queue,
    unit_of_work,
    dto,
    vehicle,
):
    vehicle.status = VehicleStatus.AVAILABLE
    vehicle_repository.get_by_id.return_value = vehicle

    with pytest.raises(VehicleNotEligibleForReconditioning):
        use_case.execute(dto)

    vehicle_repository.get_by_id.assert_called_once_with(
        "vehicle-123"
    )

    inspection_repository.get_by_vehicle_id.assert_not_called()
    reconditioning_repository.get_by_vehicle_id.assert_not_called()
    reconditioning_repository.save.assert_not_called()
    vehicle_repository.update.assert_not_called()
    job_queue.enqueue_reconditioning.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_execute_raises_when_inspection_does_not_exist(
    use_case,
    vehicle_repository,
    inspection_repository,
    reconditioning_repository,
    job_queue,
    unit_of_work,
    dto,
    vehicle,
):
    vehicle_repository.get_by_id.return_value = vehicle
    inspection_repository.get_by_vehicle_id.return_value = None

    with pytest.raises(InspectionNotFound):
        use_case.execute(dto)

    vehicle_repository.get_by_id.assert_called_once_with(
        "vehicle-123"
    )
    inspection_repository.get_by_vehicle_id.assert_called_once_with(
        "vehicle-123"
    )

    reconditioning_repository.get_by_vehicle_id.assert_not_called()
    reconditioning_repository.save.assert_not_called()
    vehicle_repository.update.assert_not_called()
    job_queue.enqueue_reconditioning.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_execute_raises_when_inspection_is_not_completed(
    use_case,
    vehicle_repository,
    inspection_repository,
    reconditioning_repository,
    job_queue,
    unit_of_work,
    dto,
    vehicle,
    inspection,
):
    vehicle_repository.get_by_id.return_value = vehicle

    inspection.status = InspectionStatus.IN_PROGRESS
    inspection_repository.get_by_vehicle_id.return_value = inspection

    with pytest.raises(InspectionNotCompleted):
        use_case.execute(dto)

    vehicle_repository.get_by_id.assert_called_once_with(
        "vehicle-123"
    )
    inspection_repository.get_by_vehicle_id.assert_called_once_with(
        "vehicle-123"
    )

    reconditioning_repository.get_by_vehicle_id.assert_not_called()
    reconditioning_repository.save.assert_not_called()
    vehicle_repository.update.assert_not_called()
    job_queue.enqueue_reconditioning.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


@pytest.mark.parametrize(
    "existing_status",
    [
        ReconditioningStatus.PENDING,
        ReconditioningStatus.IN_PROGRESS,
    ],
)
def test_execute_raises_when_reconditioning_is_already_running(
    use_case,
    vehicle_repository,
    inspection_repository,
    reconditioning_repository,
    job_queue,
    unit_of_work,
    dto,
    vehicle,
    inspection,
    existing_status,
):
    configure_success(
        vehicle_repository,
        inspection_repository,
        reconditioning_repository,
        vehicle,
        inspection,
    )

    existing = Mock()
    existing.status = existing_status

    reconditioning_repository.get_by_vehicle_id.return_value = existing

    with pytest.raises(ReconditioningAlreadyRunning):
        use_case.execute(dto)

    reconditioning_repository.get_by_vehicle_id.assert_called_once_with(
        "vehicle-123"
    )

    reconditioning_repository.save.assert_not_called()
    vehicle_repository.update.assert_not_called()
    vehicle.start_reconditioning.assert_not_called()
    job_queue.enqueue_reconditioning.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_execute_rolls_back_when_queue_fails(
    use_case,
    vehicle_repository,
    inspection_repository,
    reconditioning_repository,
    job_queue,
    unit_of_work,
    dto,
    vehicle,
    inspection,
):
    configure_success(
        vehicle_repository,
        inspection_repository,
        reconditioning_repository,
        vehicle,
        inspection,
    )

    reconditioning = SimpleNamespace(
        id="reconditioning-123",
        vehicle_id="vehicle-123",
        status=ReconditioningStatus.PENDING,
    )

    job_queue.enqueue_reconditioning.side_effect = RuntimeError(
        "Queue unavailable"
    )

    with patch(
        "modules.reconditionings.application.use_cases.admin.start_reconditioning.Reconditioning.create",
        return_value=reconditioning,
    ):
        with pytest.raises(
            RuntimeError,
            match="Queue unavailable",
        ):
            use_case.execute(dto)

    reconditioning_repository.save.assert_called_once_with(
        reconditioning
    )
    vehicle_repository.update.assert_called_once_with(
        vehicle
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()

    job_queue.enqueue_reconditioning.assert_called_once_with(
        "reconditioning-123",
        "admin-123",
    )