from unittest.mock import Mock

import pytest

from modules.vehicles.application.dtos.admin.create_vehicle_dto import (
    CreateVehicleDTO,
)
from modules.vehicles.application.use_cases.admin.create_vehicle import (
    CreateVehicleUseCase,
)
from modules.vehicles.domain.enums import (
    EngineType,
    VehicleCondition,
    VehicleStatus,
    VehicleType,
)
from modules.vehicles.domain.exceptions import (
    VehicleAlreadyExists,
)
from modules.warranties.domain.exceptions import (
    WarrantyRequiredForSale,
)
from modules.applications.domain.enums import EventType
from modules.vehicles.domain.utils.license_plate import (
    normalize_license_plate,
)


# ============================================================
# HELPERS
# ============================================================


def make_dto(
    *,
    vehicle_type=VehicleType.SALE,
    license_plate="AB-123-CD",
    warranty_plan_id="warranty-plan-1",
    included_options=None,
    optional_options=None,
):
    return CreateVehicleDTO(
        brand="BMW",
        model="Serie 3",
        price=30000.0,
        type=vehicle_type,
        mileage=50000,
        year=2022,
        description="Véhicule en très bon état",
        engine_type=next(iter(EngineType)),
        equipments=["GPS", "Climatisation"],
        condition=next(iter(VehicleCondition)),
        images=["image1.jpg", "image2.jpg"],
        license_plate=license_plate,
        warranty_plan_id=warranty_plan_id,
        included_options=included_options or [],
        optional_options=optional_options or [],
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def vehicle_repository():
    repo = Mock()
    repo.get_by_license_plate.return_value = None
    return repo


@pytest.fixture
def warranty_repository():
    return Mock()


@pytest.fixture
def assign_options_usecase():
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
    warranty_repository,
    assign_options_usecase,
    event_service,
    uow,
):
    return CreateVehicleUseCase(
        vehicle_repository=vehicle_repository,
        warranty_repository=warranty_repository,
        assign_options_usecase=assign_options_usecase,
        event_service=event_service,
        unit_of_work=uow,
    )


# ============================================================
# SUCCESS — SALE
# ============================================================


def test_create_sale_vehicle_success(
    use_case,
    vehicle_repository,
    warranty_repository,
    assign_options_usecase,
    event_service,
    uow,
):
    dto = make_dto(
        vehicle_type=VehicleType.SALE,
        warranty_plan_id="warranty-plan-1",
        included_options=["option-1"],
        optional_options=["option-2"],
    )

    saved_vehicle = Mock(
        id="vehicle-1",
        brand="BMW",
        model="Serie 3",
    )

    vehicle_repository.save.return_value = saved_vehicle

    result = use_case.execute(
        dto=dto,
        admin_id="admin-1",
    )

    assert result is saved_vehicle

    vehicle_repository.save.assert_called_once()
    warranty_repository.save.assert_called_once()

    assign_options_usecase.execute.assert_called_once_with(
        vehicle_id="vehicle-1",
        included_option_ids=["option-1"],
        optional_option_ids=["option-2"],
    )

    event_service.log.assert_called_once_with(
        type=EventType.VEHICLE_CREATED,
        message="Véhicule créé",
        vehicle_id="vehicle-1",
        user_id="admin-1",
        event_metadata={
            "brand": "BMW",
            "model": "Serie 3",
        },
    )

    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()


def test_created_vehicle_has_expected_initial_state(
    use_case,
    vehicle_repository,
    warranty_repository,
):
    dto = make_dto(
        vehicle_type=VehicleType.SALE,
        warranty_plan_id="warranty-plan-1",
    )

    vehicle_repository.save.side_effect = lambda vehicle: vehicle

    result = use_case.execute(
        dto=dto,
        admin_id="admin-1",
    )

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
    assert result.images == dto.images

    assert result.is_available is False
    assert result.status == VehicleStatus.AVAILABLE

    assert result.license_plate == normalize_license_plate(
        dto.license_plate
    )

    assert result.id is not None
    assert result.warranty is not None
    assert result.warranty.vehicle_id == result.id
    assert result.warranty.warranty_plan_id == "warranty-plan-1"
    assert result.warranty.is_active is False


# ============================================================
# SUCCESS — RENT
# ============================================================


def test_create_rental_vehicle_success(
    use_case,
    vehicle_repository,
    warranty_repository,
    assign_options_usecase,
    event_service,
    uow,
):
    dto = make_dto(
        vehicle_type=VehicleType.RENT,
        warranty_plan_id="warranty-plan-should-be-ignored",
    )

    vehicle_repository.save.side_effect = lambda vehicle: vehicle

    result = use_case.execute(
        dto=dto,
        admin_id="admin-1",
    )

    assert result.type == VehicleType.RENT

    assert result.warranty is None

    warranty_repository.save.assert_not_called()

    vehicle_repository.save.assert_called_once()
    assign_options_usecase.execute.assert_called_once()

    event_service.log.assert_called_once()

    uow.commit.assert_called_once()


def test_rental_vehicle_does_not_use_warranty_plan(
    use_case,
    vehicle_repository,
    warranty_repository,
):
    dto = make_dto(
        vehicle_type=VehicleType.RENT,
        warranty_plan_id="warranty-plan-1",
    )

    vehicle_repository.save.side_effect = lambda vehicle: vehicle

    result = use_case.execute(
        dto=dto,
        admin_id="admin-1",
    )

    assert result.warranty is None
    warranty_repository.save.assert_not_called()


# ============================================================
# DUPLICATE LICENSE PLATE
# ============================================================


def test_duplicate_license_plate_is_rejected(
    use_case,
    vehicle_repository,
    warranty_repository,
    assign_options_usecase,
    event_service,
    uow,
):
    dto = make_dto(
        license_plate="AB-123-CD",
    )

    existing_vehicle = Mock(
        id="existing-vehicle",
    )

    vehicle_repository.get_by_license_plate.return_value = (
        existing_vehicle
    )

    with pytest.raises(VehicleAlreadyExists):
        use_case.execute(
            dto=dto,
            admin_id="admin-1",
        )

    vehicle_repository.get_by_license_plate.assert_called_once_with(
        normalize_license_plate("AB-123-CD")
    )

    vehicle_repository.save.assert_not_called()
    warranty_repository.save.assert_not_called()
    assign_options_usecase.execute.assert_not_called()
    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_license_plate_is_normalized_before_duplicate_check(
    use_case,
    vehicle_repository,
):
    dto = make_dto(
        license_plate=" ab-123-cd ",
    )

    vehicle_repository.get_by_license_plate.return_value = None
    vehicle_repository.save.side_effect = lambda vehicle: vehicle

    use_case.execute(
        dto=dto,
        admin_id="admin-1",
    )

    expected_license_plate = normalize_license_plate(
        " ab-123-cd "
    )

    vehicle_repository.get_by_license_plate.assert_called_once_with(
        expected_license_plate
    )


# ============================================================
# NO LICENSE PLATE
# ============================================================


def test_no_license_plate_skips_duplicate_check(
    use_case,
    vehicle_repository,
):
    dto = make_dto(
        license_plate=None,
    )

    vehicle_repository.save.side_effect = lambda vehicle: vehicle

    result = use_case.execute(
        dto=dto,
        admin_id="admin-1",
    )

    vehicle_repository.get_by_license_plate.assert_not_called()

    assert result.license_plate is None


# ============================================================
# WARRANTY BUSINESS RULE
# ============================================================


def test_sale_vehicle_requires_warranty(
    use_case,
    vehicle_repository,
    warranty_repository,
    assign_options_usecase,
    event_service,
    uow,
):
    dto = make_dto(
        vehicle_type=VehicleType.SALE,
        warranty_plan_id=None,
    )

    with pytest.raises(WarrantyRequiredForSale):
        use_case.execute(
            dto=dto,
            admin_id="admin-1",
        )

    vehicle_repository.save.assert_not_called()
    warranty_repository.save.assert_not_called()
    assign_options_usecase.execute.assert_not_called()
    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


# ============================================================
# OPTIONS
# ============================================================


def test_options_are_assigned(
    use_case,
    vehicle_repository,
    assign_options_usecase,
):
    dto = make_dto(
        included_options=["included-1", "included-2"],
        optional_options=["optional-1"],
    )

    saved_vehicle = Mock(id="vehicle-1")

    vehicle_repository.save.return_value = saved_vehicle

    use_case.execute(
        dto=dto,
        admin_id="admin-1",
    )

    assign_options_usecase.execute.assert_called_once_with(
        vehicle_id="vehicle-1",
        included_option_ids=[
            "included-1",
            "included-2",
        ],
        optional_option_ids=[
            "optional-1",
        ],
    )


def test_empty_options_are_supported(
    use_case,
    vehicle_repository,
    assign_options_usecase,
):
    dto = make_dto(
        included_options=[],
        optional_options=[],
    )

    vehicle_repository.save.return_value = Mock(
        id="vehicle-1",
    )

    use_case.execute(
        dto=dto,
        admin_id="admin-1",
    )

    assign_options_usecase.execute.assert_called_once_with(
        vehicle_id="vehicle-1",
        included_option_ids=[],
        optional_option_ids=[],
    )


# ============================================================
# WARRANTY
# ============================================================


def test_warranty_is_created_and_saved_for_sale(
    use_case,
    vehicle_repository,
    warranty_repository,
):
    dto = make_dto(
        vehicle_type=VehicleType.SALE,
        warranty_plan_id="plan-42",
    )

    vehicle_repository.save.side_effect = lambda vehicle: vehicle

    result = use_case.execute(
        dto=dto,
        admin_id="admin-1",
    )

    warranty = result.warranty

    assert warranty is not None
    assert warranty.id is not None
    assert warranty.vehicle_id == result.id
    assert warranty.warranty_plan_id == "plan-42"
    assert warranty.is_active is False

    warranty_repository.save.assert_called_once_with(
        warranty
    )


# ============================================================
# EVENT
# ============================================================


def test_vehicle_created_event_is_logged(
    use_case,
    vehicle_repository,
    event_service,
):
    dto = make_dto()

    saved_vehicle = Mock(
        id="vehicle-123",
        brand="BMW",
        model="Serie 3",
    )

    vehicle_repository.save.return_value = saved_vehicle

    use_case.execute(
        dto=dto,
        admin_id="admin-42",
    )

    event_service.log.assert_called_once_with(
        type=EventType.VEHICLE_CREATED,
        message="Véhicule créé",
        vehicle_id="vehicle-123",
        user_id="admin-42",
        event_metadata={
            "brand": "BMW",
            "model": "Serie 3",
        },
    )


# ============================================================
# ROLLBACK / ERRORS
# ============================================================


def test_vehicle_repository_error_rolls_back(
    use_case,
    vehicle_repository,
    uow,
):
    dto = make_dto()

    vehicle_repository.save.side_effect = RuntimeError(
        "vehicle save error"
    )

    with pytest.raises(
        RuntimeError,
        match="vehicle save error",
    ):
        use_case.execute(
            dto=dto,
            admin_id="admin-1",
        )

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_warranty_repository_error_rolls_back(
    use_case,
    vehicle_repository,
    warranty_repository,
    uow,
):
    dto = make_dto(
        vehicle_type=VehicleType.SALE,
        warranty_plan_id="plan-1",
    )

    warranty_repository.save.side_effect = RuntimeError(
        "warranty save error"
    )

    with pytest.raises(
        RuntimeError,
        match="warranty save error",
    ):
        use_case.execute(
            dto=dto,
            admin_id="admin-1",
        )

    vehicle_repository.save.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_option_assignment_error_rolls_back(
    use_case,
    vehicle_repository,
    assign_options_usecase,
    uow,
):
    dto = make_dto()

    vehicle_repository.save.return_value = Mock(
        id="vehicle-1",
    )

    assign_options_usecase.execute.side_effect = RuntimeError(
        "option assignment error"
    )

    with pytest.raises(
        RuntimeError,
        match="option assignment error",
    ):
        use_case.execute(
            dto=dto,
            admin_id="admin-1",
        )

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_event_error_rolls_back(
    use_case,
    vehicle_repository,
    event_service,
    uow,
):
    dto = make_dto()

    vehicle_repository.save.return_value = Mock(
        id="vehicle-1",
        brand="BMW",
        model="Serie 3",
    )

    event_service.log.side_effect = RuntimeError(
        "event error"
    )

    with pytest.raises(
        RuntimeError,
        match="event error",
    ):
        use_case.execute(
            dto=dto,
            admin_id="admin-1",
        )

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_commit_error_rolls_back(
    use_case,
    vehicle_repository,
    uow,
):
    dto = make_dto()

    vehicle_repository.save.return_value = Mock(
        id="vehicle-1",
        brand="BMW",
        model="Serie 3",
    )

    uow.commit.side_effect = RuntimeError(
        "commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="commit error",
    ):
        use_case.execute(
            dto=dto,
            admin_id="admin-1",
        )

    uow.commit.assert_called_once()
    uow.rollback.assert_called_once()


# ============================================================
# NO UNEXPECTED WRITES AFTER VALIDATION FAILURE
# ============================================================


def test_warranty_validation_happens_before_vehicle_save(
    use_case,
    vehicle_repository,
):
    dto = make_dto(
        vehicle_type=VehicleType.SALE,
        warranty_plan_id=None,
    )

    with pytest.raises(WarrantyRequiredForSale):
        use_case.execute(
            dto=dto,
            admin_id="admin-1",
        )

    vehicle_repository.save.assert_not_called()


def test_duplicate_validation_happens_before_vehicle_save(
    use_case,
    vehicle_repository,
):
    dto = make_dto()

    vehicle_repository.get_by_license_plate.return_value = Mock(
        id="existing-vehicle",
    )

    with pytest.raises(VehicleAlreadyExists):
        use_case.execute(
            dto=dto,
            admin_id="admin-1",
        )

    vehicle_repository.save.assert_not_called()