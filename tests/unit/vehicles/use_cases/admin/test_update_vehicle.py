from unittest.mock import Mock

import pytest
from unittest.mock import call
from modules.vehicles.application.use_cases.admin.update_vehicle import (
    UpdateVehicleUseCase,
)
from modules.vehicles.application.dtos.admin.update_vehicle_dto import (
    UpdateVehicleDTO,
)
from modules.vehicles.domain.enums import (
    EngineType,
    VehicleCondition,
    VehicleStatus,
    VehicleType,
)
from modules.vehicles.domain.exceptions import (
    VehicleAlreadyExists,
    VehicleNotFound,
)
from modules.warranties.domain.exceptions import (
    WarrantyNotAllowedForRental,
    WarrantyRequiredForSale,
)
from modules.applications.domain.enums import EventType


# ============================================================
# HELPERS
# ============================================================


def make_dto(
    *,
    vehicle_id="vehicle-1",
    admin_id="admin-1",
    vehicle_type=VehicleType.SALE,
    warranty_plan_id="plan-1",
    license_plate="AB-123-CD",
    images=None,
    included_options=None,
    optional_options=None,
):
    return UpdateVehicleDTO(
        vehicle_id=vehicle_id,
        admin_id=admin_id,
        brand="BMW",
        model="Serie 3",
        price=30000.0,
        type=vehicle_type,
        mileage=50000,
        year=2022,
        description="Véhicule mis à jour",
        engine_type=next(iter(EngineType)),
        equipments=["GPS", "Climatisation"],
        condition=next(iter(VehicleCondition)),
        images=images,
        license_plate=license_plate,
        warranty_plan_id=warranty_plan_id,
        included_options=(
            included_options
            if included_options is not None
            else ["option-1"]
        ),
        optional_options=(
            optional_options
            if optional_options is not None
            else ["option-2"]
        ),
    )


def make_vehicle(
    *,
    vehicle_id="vehicle-1",
    images=None,
    vehicle_type=VehicleType.SALE,
):
    vehicle = Mock(
        id=vehicle_id,
        brand="Audi",
        model="A3",
        price=20000.0,
        type=vehicle_type,
        mileage=70000,
        year=2020,
        description="Ancienne description",
        engine_type=next(iter(EngineType)),
        equipments=["GPS"],
        condition=next(iter(VehicleCondition)),
        license_plate="AA-111-AA",
        status=VehicleStatus.AVAILABLE,
    )

    vehicle.images = (
        images
        if images is not None
        else [
            "images/old-1.jpg",
            "images/old-2.jpg",
        ]
    )

    return vehicle


def make_warranty(
    *,
    warranty_id="warranty-1",
    vehicle_id="vehicle-1",
    warranty_plan_id="old-plan",
):
    return Mock(
        id=warranty_id,
        vehicle_id=vehicle_id,
        warranty_plan_id=warranty_plan_id,
        is_active=False,
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def repository():
    repo = Mock()
    repo.get_by_license_plate.return_value = None
    return repo


@pytest.fixture
def vehicle_warranty_repository():
    return Mock()


@pytest.fixture
def assign_options_uc():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def s3_service():
    return Mock()


@pytest.fixture
def use_case(
    repository,
    vehicle_warranty_repository,
    assign_options_uc,
    event_service,
    unit_of_work,
    s3_service,
):
    return UpdateVehicleUseCase(
        repo=repository,
        vehicle_warranty_repository=vehicle_warranty_repository,
        assign_options_uc=assign_options_uc,
        event_service=event_service,
        unit_of_work=unit_of_work,
        s3_service=s3_service,
    )


@pytest.fixture
def vehicle(repository):
    vehicle = make_vehicle()

    repository.get_by_id.return_value = vehicle

    return vehicle


# ============================================================
# SUCCESS
# ============================================================


def test_update_vehicle_success(
    use_case,
    repository,
    vehicle_warranty_repository,
    assign_options_uc,
    event_service,
    unit_of_work,
    s3_service,
    vehicle,
):
    dto = make_dto()

    vehicle_warranty_repository.get_by_vehicle_id.return_value = None

    result = use_case.execute(dto)

    assert result is vehicle

    repository.get_by_id.assert_called_once_with(
        "vehicle-1"
    )

    repository.update.assert_called_once_with(
        vehicle
    )

    assign_options_uc.execute.assert_called_once_with(
        vehicle_id="vehicle-1",
        included_option_ids=["option-1"],
        optional_option_ids=["option-2"],
    )

    event_service.log.assert_called_once_with(
        type=EventType.VEHICLE_UPDATED,
        message="Informations véhicule mises à jour",
        vehicle_id="vehicle-1",
        user_id="admin-1",
        event_metadata={
            "updated_fields": [
                "brand",
                "model",
                "price",
                "type",
                "mileage",
                "year",
                "description",
                "engine_type",
                "equipments",
                "condition",
                "license_plate",
                "images",
            ],
        },
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()

    s3_service.delete_file.assert_any_call(
        "images/old-1.jpg"
    )
    s3_service.delete_file.assert_any_call(
        "images/old-2.jpg"
    )


# ============================================================
# VEHICLE FIELDS
# ============================================================


def test_vehicle_fields_are_updated(
    use_case,
    vehicle,
):
    dto = make_dto(
        vehicle_type=VehicleType.SALE,
        license_plate="BB-222-BB",
        images=["images/new.jpg"],
    )

    result = use_case.execute(dto)

    assert result.brand == dto.brand
    assert result.model == dto.model
    assert result.price == dto.price
    assert result.type == dto.type
    assert result.mileage == dto.mileage
    assert result.year == dto.year
    assert result.description == dto.description
    assert result.engine_type == dto.engine_type
    assert result.equipments == dto.equipments
    assert result.condition == dto.condition
    assert result.license_plate == "BB-222-BB"
    assert result.images == ["images/new.jpg"]


def test_vehicle_id_is_used_to_load_vehicle(
    use_case,
    repository,
):
    vehicle = make_vehicle(vehicle_id="vehicle-42")
    repository.get_by_id.return_value = vehicle

    dto = make_dto(
        vehicle_id="vehicle-42",
    )

    use_case.execute(dto)

    repository.get_by_id.assert_called_once_with(
        "vehicle-42"
    )


# ============================================================
# VEHICLE NOT FOUND
# ============================================================


def test_vehicle_not_found(
    use_case,
    repository,
    vehicle_warranty_repository,
    assign_options_uc,
    event_service,
    unit_of_work,
):
    repository.get_by_id.return_value = None

    dto = make_dto()

    with pytest.raises(VehicleNotFound):
        use_case.execute(dto)

    repository.get_by_id.assert_called_once_with(
        "vehicle-1"
    )

    repository.update.assert_not_called()
    vehicle_warranty_repository.get_by_vehicle_id.assert_not_called()
    assign_options_uc.execute.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# LICENSE PLATE
# ============================================================


def test_license_plate_is_normalized(
    use_case,
    repository,
    vehicle,
):
    dto = make_dto(
        license_plate=" ab-123-cd ",
    )

    repository.get_by_license_plate.return_value = None

    use_case.execute(dto)

    repository.get_by_license_plate.assert_called_once_with(
        "AB-123-CD"
    )


def test_duplicate_license_plate_is_rejected(
    use_case,
    repository,
    vehicle,
    vehicle_warranty_repository,
    assign_options_uc,
    event_service,
    unit_of_work,
):
    existing_vehicle = make_vehicle(
        vehicle_id="vehicle-2"
    )

    repository.get_by_license_plate.return_value = (
        existing_vehicle
    )

    dto = make_dto(
        license_plate="BB-222-BB",
    )

    with pytest.raises(VehicleAlreadyExists):
        use_case.execute(dto)

    repository.update.assert_not_called()
    vehicle_warranty_repository.get_by_vehicle_id.assert_not_called()
    assign_options_uc.execute.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_same_vehicle_license_plate_is_allowed(
    use_case,
    repository,
    vehicle,
):
    repository.get_by_license_plate.return_value = vehicle

    dto = make_dto(
        license_plate="AA-111-AA",
    )

    result = use_case.execute(dto)

    assert result is vehicle
    repository.update.assert_called_once_with(vehicle)


def test_no_license_plate_skips_duplicate_check(
    use_case,
    repository,
    vehicle,
):
    dto = make_dto(
        license_plate=None,
    )

    use_case.execute(dto)

    repository.get_by_license_plate.assert_not_called()
    assert vehicle.license_plate is None


# ============================================================
# WARRANTY — SALE
# ============================================================


def test_sale_requires_warranty(
    use_case,
    repository,
    vehicle,
    vehicle_warranty_repository,
    assign_options_uc,
    event_service,
    unit_of_work,
):
    dto = make_dto(
        vehicle_type=VehicleType.SALE,
        warranty_plan_id=None,
    )

    with pytest.raises(WarrantyRequiredForSale):
        use_case.execute(dto)

    vehicle_warranty_repository.get_by_vehicle_id.assert_not_called()
    repository.update.assert_not_called()
    assign_options_uc.execute.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# WARRANTY — RENT
# ============================================================


def test_rental_cannot_have_warranty(
    use_case,
    repository,
    vehicle,
    vehicle_warranty_repository,
    assign_options_uc,
    event_service,
    unit_of_work,
):
    dto = make_dto(
        vehicle_type=VehicleType.RENT,
        warranty_plan_id="plan-1",
    )

    with pytest.raises(WarrantyNotAllowedForRental):
        use_case.execute(dto)

    vehicle_warranty_repository.get_by_vehicle_id.assert_not_called()
    repository.update.assert_not_called()
    assign_options_uc.execute.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# WARRANTY — DELETE
# ============================================================


def test_existing_warranty_is_deleted_when_plan_is_removed(
    use_case,
    vehicle,
    vehicle_warranty_repository,
):
    warranty = make_warranty()

    vehicle_warranty_repository.get_by_vehicle_id.return_value = (
        warranty
    )

    dto = make_dto(
        vehicle_type=VehicleType.RENT,
        warranty_plan_id=None,
    )

    use_case.execute(dto)

    vehicle_warranty_repository.delete.assert_called_once_with(
        "warranty-1"
    )

    vehicle_warranty_repository.save.assert_not_called()
    vehicle_warranty_repository.update.assert_not_called()


def test_no_warranty_is_deleted_when_none_exists(
    use_case,
    vehicle,
    vehicle_warranty_repository,
):
    vehicle_warranty_repository.get_by_vehicle_id.return_value = None

    dto = make_dto(
        vehicle_type=VehicleType.RENT,
        warranty_plan_id=None,
    )

    use_case.execute(dto)

    vehicle_warranty_repository.delete.assert_not_called()
    vehicle_warranty_repository.save.assert_not_called()
    vehicle_warranty_repository.update.assert_not_called()


# ============================================================
# WARRANTY — CREATE
# ============================================================


def test_warranty_is_created_when_plan_is_added(
    use_case,
    vehicle,
    vehicle_warranty_repository,
):
    vehicle_warranty_repository.get_by_vehicle_id.return_value = None

    dto = make_dto(
        vehicle_type=VehicleType.SALE,
        warranty_plan_id="new-plan",
    )

    use_case.execute(dto)

    vehicle_warranty_repository.save.assert_called_once()

    warranty = (
        vehicle_warranty_repository
        .save
        .call_args.args[0]
    )

    assert isinstance(
        warranty,
        type(
            vehicle_warranty_repository
            .save
            .call_args.args[0]
        ),
    )

    assert warranty.vehicle_id == "vehicle-1"
    assert warranty.warranty_plan_id == "new-plan"
    assert warranty.is_active is False
    assert warranty.id is not None


# ============================================================
# WARRANTY — UPDATE
# ============================================================


def test_existing_warranty_is_updated(
    use_case,
    vehicle,
    vehicle_warranty_repository,
):
    warranty = make_warranty(
        warranty_plan_id="old-plan"
    )

    vehicle_warranty_repository.get_by_vehicle_id.return_value = (
        warranty
    )

    dto = make_dto(
        vehicle_type=VehicleType.SALE,
        warranty_plan_id="new-plan",
    )

    use_case.execute(dto)

    assert warranty.warranty_plan_id == "new-plan"

    vehicle_warranty_repository.update.assert_called_once_with(
        warranty
    )

    vehicle_warranty_repository.save.assert_not_called()
    vehicle_warranty_repository.delete.assert_not_called()


# ============================================================
# IMAGES
# ============================================================


def test_removed_images_are_deleted_from_s3(
    use_case,
    vehicle,
    s3_service,
):
    vehicle.images = [
        "images/old-1.jpg",
        "images/old-2.jpg",
        "images/keep.jpg",
    ]

    dto = make_dto(
        images=[
            "images/keep.jpg",
            "images/new.jpg",
        ],
    )

    use_case.execute(dto)

    assert s3_service.delete_file.call_count == 2

    s3_service.delete_file.assert_any_call(
        "images/old-1.jpg"
    )

    s3_service.delete_file.assert_any_call(
        "images/old-2.jpg"
    )

    assert call("images/keep.jpg") not in (
    s3_service.delete_file.call_args_list
)


def test_new_images_are_not_deleted(
    use_case,
    vehicle,
    s3_service,
):
    vehicle.images = [
        "images/old.jpg",
    ]

    dto = make_dto(
        images=[
            "images/new.jpg",
        ],
    )

    use_case.execute(dto)

    s3_service.delete_file.assert_called_once_with(
        "images/old.jpg"
    )


def test_same_images_do_not_trigger_s3_deletion(
    use_case,
    vehicle,
    s3_service,
):
    vehicle.images = [
        "images/one.jpg",
        "images/two.jpg",
    ]

    dto = make_dto(
        images=[
            "images/one.jpg",
            "images/two.jpg",
        ],
    )

    use_case.execute(dto)

    s3_service.delete_file.assert_not_called()


def test_none_old_images_are_supported(
    use_case,
    vehicle,
    s3_service,
):
    vehicle.images = None

    dto = make_dto(
        images=["images/new.jpg"],
    )

    use_case.execute(dto)

    s3_service.delete_file.assert_not_called()


def test_none_new_images_are_supported(
    use_case,
    vehicle,
    s3_service,
):
    vehicle.images = [
        "images/old.jpg",
    ]

    dto = make_dto(
        images=None,
    )

    use_case.execute(dto)

    assert vehicle.images == []

    s3_service.delete_file.assert_called_once_with(
        "images/old.jpg"
    )


# ============================================================
# OPTIONS
# ============================================================


def test_options_are_reassigned(
    use_case,
    assign_options_uc,
    vehicle,
):
    dto = make_dto(
        included_options=[
            "included-1",
            "included-2",
        ],
        optional_options=[
            "optional-1",
        ],
    )

    use_case.execute(dto)

    assign_options_uc.execute.assert_called_once_with(
        vehicle_id="vehicle-1",
        included_option_ids=[
            "included-1",
            "included-2",
        ],
        optional_option_ids=[
            "optional-1",
        ],
    )


# ============================================================
# EVENT
# ============================================================


def test_vehicle_updated_event_is_logged(
    use_case,
    event_service,
    vehicle,
):
    dto = make_dto()

    use_case.execute(dto)

    event_service.log.assert_called_once_with(
        type=EventType.VEHICLE_UPDATED,
        message="Informations véhicule mises à jour",
        vehicle_id="vehicle-1",
        user_id="admin-1",
        event_metadata={
            "updated_fields": [
                "brand",
                "model",
                "price",
                "type",
                "mileage",
                "year",
                "description",
                "engine_type",
                "equipments",
                "condition",
                "license_plate",
                "images",
            ],
        },
    )


# ============================================================
# COMMIT
# ============================================================


def test_commit_is_called(
    use_case,
    unit_of_work,
    vehicle,
):
    dto = make_dto()

    use_case.execute(dto)

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# ROLLBACK — REPOSITORY
# ============================================================


def test_vehicle_update_error_rolls_back(
    use_case,
    repository,
    unit_of_work,
    vehicle,
):
    repository.update.side_effect = RuntimeError(
        "update error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="update error",
    ):
        use_case.execute(dto)

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_warranty_save_error_rolls_back(
    use_case,
    vehicle,
    vehicle_warranty_repository,
    unit_of_work,
):
    vehicle_warranty_repository.get_by_vehicle_id.return_value = None

    vehicle_warranty_repository.save.side_effect = RuntimeError(
        "warranty save error"
    )

    dto = make_dto(
        vehicle_type=VehicleType.SALE,
        warranty_plan_id="plan-1",
    )

    with pytest.raises(
        RuntimeError,
        match="warranty save error",
    ):
        use_case.execute(dto)

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_warranty_update_error_rolls_back(
    use_case,
    vehicle,
    vehicle_warranty_repository,
    unit_of_work,
):
    warranty = make_warranty()

    vehicle_warranty_repository.get_by_vehicle_id.return_value = (
        warranty
    )

    vehicle_warranty_repository.update.side_effect = RuntimeError(
        "warranty update error"
    )

    dto = make_dto(
        vehicle_type=VehicleType.SALE,
        warranty_plan_id="new-plan",
    )

    with pytest.raises(
        RuntimeError,
        match="warranty update error",
    ):
        use_case.execute(dto)

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_option_assignment_error_rolls_back(
    use_case,
    assign_options_uc,
    unit_of_work,
    vehicle,
):
    assign_options_uc.execute.side_effect = RuntimeError(
        "option assignment error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="option assignment error",
    ):
        use_case.execute(dto)

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_event_error_rolls_back(
    use_case,
    event_service,
    unit_of_work,
    vehicle,
):
    event_service.log.side_effect = RuntimeError(
        "event error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="event error",
    ):
        use_case.execute(dto)

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_commit_error_rolls_back(
    use_case,
    unit_of_work,
    vehicle,
):
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


# ============================================================
# S3 ERROR
# ============================================================


def test_s3_deletion_error_is_propagated_and_rolls_back(
    use_case,
    s3_service,
    unit_of_work,
    vehicle,
):
    vehicle.images = [
        "images/old.jpg",
    ]

    dto = make_dto(
        images=["images/new.jpg"],
    )

    s3_service.delete_file.side_effect = RuntimeError(
        "s3 error"
    )

    with pytest.raises(
        RuntimeError,
        match="s3 error",
    ):
        use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()

    # Important : the code commits BEFORE deleting old S3 files.
    unit_of_work.commit.assert_called_once()


# ============================================================
# NO UNEXPECTED OPERATIONS
# ============================================================


def test_warranty_validation_happens_before_update(
    use_case,
    repository,
    vehicle,
):
    dto = make_dto(
        vehicle_type=VehicleType.SALE,
        warranty_plan_id=None,
    )

    with pytest.raises(WarrantyRequiredForSale):
        use_case.execute(dto)

    repository.update.assert_not_called()


def test_rental_warranty_validation_happens_before_update(
    use_case,
    repository,
    vehicle,
):
    dto = make_dto(
        vehicle_type=VehicleType.RENT,
        warranty_plan_id="plan-1",
    )

    with pytest.raises(WarrantyNotAllowedForRental):
        use_case.execute(dto)

    repository.update.assert_not_called()