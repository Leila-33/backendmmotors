from unittest.mock import Mock

import pytest

from modules.vehicles.application.dtos.admin.vehicle_admin_action_dto import (
    VehicleAdminActionDTO,
)
from modules.vehicles.application.results.admin.delete_vehicle_result import (
    DeleteVehicleResult,
)
from modules.vehicles.application.use_cases.admin.delete_vehicle import (
    DeleteVehicleUseCase,
)
from modules.vehicles.domain.entities.vehicle import Vehicle
from modules.vehicles.domain.exceptions import VehicleNotFound
from modules.applications.domain.enums import EventType
from modules.vehicles.domain.enums import VehicleType
# ============================================================
# HELPERS
# ============================================================


def make_vehicle(
    *,
    vehicle_id="vehicle-1",
    brand="BMW",
    model="Serie 3",
    images=None,
):
    return Vehicle(
        id=vehicle_id,
        brand=brand,
        model=model,
        price=30000.0,
        mileage=50000,
        year=2022,
        images=images or [],
        type=VehicleType.SALE
    )


def make_dto(
    *,
    vehicle_id="vehicle-1",
    admin_id="admin-1",
):
    return VehicleAdminActionDTO(
        vehicle_id=vehicle_id,
        admin_id=admin_id,
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def vehicle_repository():
    return Mock()


@pytest.fixture
def s3_service():
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
    s3_service,
    event_service,
    uow,
):
    return DeleteVehicleUseCase(
        repository=vehicle_repository,
        s3_service=s3_service,
        event_service=event_service,
        unit_of_work=uow,
    )


# ============================================================
# VEHICLE NOT FOUND
# ============================================================


def test_vehicle_not_found(
    use_case,
    vehicle_repository,
    s3_service,
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

    vehicle_repository.has_business_history.assert_not_called()
    vehicle_repository.update.assert_not_called()
    vehicle_repository.delete.assert_not_called()

    s3_service.delete_file.assert_not_called()
    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


# ============================================================
# ARCHIVE — BUSINESS HISTORY
# ============================================================


def test_vehicle_with_business_history_is_archived(
    use_case,
    vehicle_repository,
    event_service,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle_repository.get_by_id.return_value = vehicle
    vehicle_repository.has_business_history.return_value = True

    result = use_case.execute(dto)

    assert isinstance(
        result,
        DeleteVehicleResult,
    )

    assert result.vehicle_id == "vehicle-1"
    assert result.action == "ARCHIVED"

    vehicle_repository.get_by_id.assert_called_once_with(
        "vehicle-1"
    )

    vehicle_repository.has_business_history.assert_called_once_with(
        "vehicle-1"
    )

    vehicle_repository.update.assert_called_once_with(
        vehicle
    )

    vehicle_repository.delete.assert_not_called()

    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()


def test_vehicle_archive_method_is_called(
    use_case,
    vehicle_repository,
):
    dto = make_dto()

    vehicle = make_vehicle()

    # Mock archive explicitly so we can verify the domain method.
    vehicle.archive = Mock()

    vehicle_repository.get_by_id.return_value = vehicle
    vehicle_repository.has_business_history.return_value = True

    use_case.execute(dto)

    vehicle.archive.assert_called_once()


def test_archived_vehicle_generates_event(
    use_case,
    vehicle_repository,
    event_service,
):
    dto = make_dto(
        admin_id="admin-42",
    )

    vehicle = make_vehicle(
        brand="Audi",
        model="A4",
    )

    vehicle_repository.get_by_id.return_value = vehicle
    vehicle_repository.has_business_history.return_value = True

    use_case.execute(dto)

    event_service.log.assert_called_once_with(
        type=EventType.VEHICLE_ARCHIVED,
        message="Véhicule archivé",
        vehicle_id="vehicle-1",
        user_id="admin-42",
        event_metadata={
            "brand": "Audi",
            "model": "A4",
            "reason": "business_history",
        },
    )


def test_archive_branch_does_not_delete_s3_images(
    use_case,
    vehicle_repository,
    s3_service,
):
    dto = make_dto()

    vehicle = make_vehicle(
        images=[
            "vehicles/vehicle-1/image1.jpg",
            "vehicles/vehicle-1/image2.jpg",
        ]
    )

    vehicle_repository.get_by_id.return_value = vehicle
    vehicle_repository.has_business_history.return_value = True

    use_case.execute(dto)

    s3_service.delete_file.assert_not_called()


# ============================================================
# HARD DELETE
# ============================================================


def test_vehicle_without_business_history_is_deleted(
    use_case,
    vehicle_repository,
    s3_service,
    event_service,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle_repository.get_by_id.return_value = vehicle
    vehicle_repository.has_business_history.return_value = False

    result = use_case.execute(dto)

    assert isinstance(
        result,
        DeleteVehicleResult,
    )

    assert result.vehicle_id == "vehicle-1"
    assert result.action == "DELETED"

    vehicle_repository.delete.assert_called_once_with(
        "vehicle-1"
    )

    vehicle_repository.update.assert_not_called()

    event_service.log.assert_not_called()

    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()


# ============================================================
# S3
# ============================================================


def test_all_vehicle_images_are_deleted_from_s3(
    use_case,
    vehicle_repository,
    s3_service,
):
    dto = make_dto()

    vehicle = make_vehicle(
        images=[
            "vehicles/vehicle-1/image1.jpg",
            "vehicles/vehicle-1/image2.jpg",
            "vehicles/vehicle-1/image3.jpg",
        ]
    )

    vehicle_repository.get_by_id.return_value = vehicle
    vehicle_repository.has_business_history.return_value = False

    use_case.execute(dto)

    assert s3_service.delete_file.call_count == 3

    s3_service.delete_file.assert_any_call(
        "vehicles/vehicle-1/image1.jpg"
    )

    s3_service.delete_file.assert_any_call(
        "vehicles/vehicle-1/image2.jpg"
    )

    s3_service.delete_file.assert_any_call(
        "vehicles/vehicle-1/image3.jpg"
    )


def test_vehicle_without_images_does_not_delete_from_s3(
    use_case,
    vehicle_repository,
    s3_service,
):
    dto = make_dto()

    vehicle = make_vehicle(
        images=[]
    )

    vehicle_repository.get_by_id.return_value = vehicle
    vehicle_repository.has_business_history.return_value = False

    use_case.execute(dto)

    s3_service.delete_file.assert_not_called()


def test_vehicle_with_none_images_does_not_delete_from_s3(
    use_case,
    vehicle_repository,
    s3_service,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle.images = None

    vehicle_repository.get_by_id.return_value = vehicle
    vehicle_repository.has_business_history.return_value = False

    use_case.execute(dto)

    s3_service.delete_file.assert_not_called()


# ============================================================
# HARD DELETE ORDER
# ============================================================


def test_s3_images_are_deleted_before_repository_delete(
    use_case,
    vehicle_repository,
    s3_service,
):
    dto = make_dto()

    vehicle = make_vehicle(
        images=[
            "vehicles/vehicle-1/image.jpg",
        ]
    )

    vehicle_repository.get_by_id.return_value = vehicle
    vehicle_repository.has_business_history.return_value = False

    call_order = []

    s3_service.delete_file.side_effect = (
        lambda key: call_order.append(
            ("s3", key)
        )
    )

    vehicle_repository.delete.side_effect = (
        lambda vehicle_id: call_order.append(
            ("repository", vehicle_id)
        )
    )

    use_case.execute(dto)

    assert call_order == [
        (
            "s3",
            "vehicles/vehicle-1/image.jpg",
        ),
        (
            "repository",
            "vehicle-1",
        ),
    ]


# ============================================================
# BUSINESS HISTORY CHECK
# ============================================================


def test_business_history_is_checked_after_vehicle_is_loaded(
    use_case,
    vehicle_repository,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle_repository.get_by_id.return_value = vehicle
    vehicle_repository.has_business_history.return_value = False

    use_case.execute(dto)

    vehicle_repository.has_business_history.assert_called_once_with(
        "vehicle-1"
    )


# ============================================================
# RESULT
# ============================================================


def test_archive_result_contains_vehicle_id_and_action(
    use_case,
    vehicle_repository,
):
    dto = make_dto()

    vehicle_repository.get_by_id.return_value = make_vehicle()
    vehicle_repository.has_business_history.return_value = True

    result = use_case.execute(dto)

    assert result.vehicle_id == "vehicle-1"
    assert result.action == "ARCHIVED"


def test_delete_result_contains_vehicle_id_and_action(
    use_case,
    vehicle_repository,
):
    dto = make_dto()

    vehicle_repository.get_by_id.return_value = make_vehicle()
    vehicle_repository.has_business_history.return_value = False

    result = use_case.execute(dto)

    assert result.vehicle_id == "vehicle-1"
    assert result.action == "DELETED"


# ============================================================
# ROLLBACK — REPOSITORY
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

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()


def test_business_history_error_rolls_back(
    use_case,
    vehicle_repository,
    uow,
):
    dto = make_dto()

    vehicle_repository.get_by_id.return_value = make_vehicle()

    vehicle_repository.has_business_history.side_effect = (
        RuntimeError(
            "history error"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="history error",
    ):
        use_case.execute(dto)

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()


# ============================================================
# ROLLBACK — ARCHIVE
# ============================================================


def test_archive_error_rolls_back(
    use_case,
    vehicle_repository,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle.archive = Mock(
        side_effect=RuntimeError(
            "archive error"
        )
    )

    vehicle_repository.get_by_id.return_value = vehicle
    vehicle_repository.has_business_history.return_value = True

    with pytest.raises(
        RuntimeError,
        match="archive error",
    ):
        use_case.execute(dto)

    vehicle_repository.update.assert_not_called()

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()


def test_archive_update_error_rolls_back(
    use_case,
    vehicle_repository,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle_repository.get_by_id.return_value = vehicle
    vehicle_repository.has_business_history.return_value = True

    vehicle_repository.update.side_effect = RuntimeError(
        "update error"
    )

    with pytest.raises(
        RuntimeError,
        match="update error",
    ):
        use_case.execute(dto)

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()


# ============================================================
# ROLLBACK — EVENT
# ============================================================


def test_archive_event_error_rolls_back(
    use_case,
    vehicle_repository,
    event_service,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle_repository.get_by_id.return_value = vehicle
    vehicle_repository.has_business_history.return_value = True

    event_service.log.side_effect = RuntimeError(
        "event error"
    )

    with pytest.raises(
        RuntimeError,
        match="event error",
    ):
        use_case.execute(dto)

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()


# ============================================================
# ROLLBACK — HARD DELETE / S3
# ============================================================


def test_s3_deletion_error_rolls_back(
    use_case,
    vehicle_repository,
    s3_service,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle(
        images=[
            "vehicles/vehicle-1/image.jpg",
        ]
    )

    vehicle_repository.get_by_id.return_value = vehicle
    vehicle_repository.has_business_history.return_value = False

    s3_service.delete_file.side_effect = RuntimeError(
        "s3 error"
    )

    with pytest.raises(
        RuntimeError,
        match="s3 error",
    ):
        use_case.execute(dto)

    vehicle_repository.delete.assert_not_called()

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()


def test_repository_delete_error_rolls_back(
    use_case,
    vehicle_repository,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle_repository.get_by_id.return_value = vehicle
    vehicle_repository.has_business_history.return_value = False

    vehicle_repository.delete.side_effect = RuntimeError(
        "delete error"
    )

    with pytest.raises(
        RuntimeError,
        match="delete error",
    ):
        use_case.execute(dto)

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()


# ============================================================
# ROLLBACK — COMMIT
# ============================================================


def test_archive_commit_error_rolls_back(
    use_case,
    vehicle_repository,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle_repository.get_by_id.return_value = vehicle
    vehicle_repository.has_business_history.return_value = True

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


def test_delete_commit_error_rolls_back(
    use_case,
    vehicle_repository,
    uow,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle_repository.get_by_id.return_value = vehicle
    vehicle_repository.has_business_history.return_value = False

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
# NO UNEXPECTED CALLS — ARCHIVE
# ============================================================


def test_archive_branch_does_not_call_hard_delete(
    use_case,
    vehicle_repository,
):
    dto = make_dto()

    vehicle_repository.get_by_id.return_value = make_vehicle()
    vehicle_repository.has_business_history.return_value = True

    use_case.execute(dto)

    vehicle_repository.delete.assert_not_called()


def test_archive_branch_does_not_call_s3(
    use_case,
    vehicle_repository,
    s3_service,
):
    dto = make_dto()

    vehicle_repository.get_by_id.return_value = make_vehicle(
        images=[
            "image1.jpg",
            "image2.jpg",
        ]
    )

    vehicle_repository.has_business_history.return_value = True

    use_case.execute(dto)

    s3_service.delete_file.assert_not_called()


# ============================================================
# NO UNEXPECTED CALLS — HARD DELETE
# ============================================================


def test_hard_delete_branch_does_not_archive(
    use_case,
    vehicle_repository,
):
    dto = make_dto()

    vehicle = make_vehicle()

    vehicle.archive = Mock()

    vehicle_repository.get_by_id.return_value = vehicle
    vehicle_repository.has_business_history.return_value = False

    use_case.execute(dto)

    vehicle.archive.assert_not_called()


def test_hard_delete_branch_does_not_generate_archive_event(
    use_case,
    vehicle_repository,
    event_service,
):
    dto = make_dto()

    vehicle_repository.get_by_id.return_value = make_vehicle()
    vehicle_repository.has_business_history.return_value = False

    use_case.execute(dto)

    event_service.log.assert_not_called()