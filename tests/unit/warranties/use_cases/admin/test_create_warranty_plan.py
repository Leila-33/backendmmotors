from unittest.mock import Mock

import pytest

from modules.warranties.application.use_cases.admin.create_warranty_plan import (
    CreateWarrantyPlanUseCase,
)
from modules.warranties.domain.entities.warranty_plan import WarrantyPlan
from modules.warranties.domain.enums import WarrantyPlanType
from modules.warranties.domain.exceptions import WarrantyPlanAlreadyExists
from modules.warranties.application.dtos.admin.create_warranty_plan_dto import (
    CreateWarrantyPlanDTO,
)


def make_dto(**overrides):
    data = {
        "name": "  Garantie   Premium  ",
        "description": "Garantie complète",
        "plan_type": WarrantyPlanType.PREMIUM,
        "duration_months": 24,
        "mileage_limit": 50000,
        "covers_engine": True,
        "covers_transmission": True,
        "covers_electronics": True,
        "covers_assistance": True,
        "covers_wear_parts": False,
        "price": 1299.99,
        "admin_id": "admin-123",
    }

    data.update(overrides)

    return CreateWarrantyPlanDTO(**data)


def make_use_case():
    repository = Mock()
    event_service = Mock()
    unit_of_work = Mock()

    use_case = CreateWarrantyPlanUseCase(
        repository=repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )

    return (
        use_case,
        repository,
        event_service,
        unit_of_work,
    )


def test_create_warranty_plan_success():
    # Arrange
    (
        use_case,
        repository,
        event_service,
        unit_of_work,
    ) = make_use_case()

    repository.find_by_name.return_value = None
    repository.find_by_plan_type.return_value = None

    dto = make_dto()

    # Act
    result = use_case.execute(dto)

    # Assert
    assert result.plan_id is not None

    repository.find_by_name.assert_called_once_with(
        "Garantie Premium"
    )

    repository.find_by_plan_type.assert_called_once_with(
        WarrantyPlanType.PREMIUM
    )

    repository.save.assert_called_once()

    plan = repository.save.call_args.args[0]

    assert isinstance(plan, WarrantyPlan)
    assert plan.name == "Garantie Premium"
    assert plan.description == "Garantie complète"
    assert plan.plan_type == WarrantyPlanType.PREMIUM
    assert plan.duration_months == 24
    assert plan.mileage_limit == 50000
    assert plan.covers_engine is True
    assert plan.covers_transmission is True
    assert plan.covers_electronics is True
    assert plan.covers_assistance is True
    assert plan.covers_wear_parts is False
    assert plan.price == 1299.99
    assert plan.active is True

    event_service.log.assert_called_once()
    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


def test_create_warranty_plan_normalizes_name():
    # Arrange
    (
        use_case,
        repository,
        event_service,
        unit_of_work,
    ) = make_use_case()

    repository.find_by_name.return_value = None
    repository.find_by_plan_type.return_value = None

    dto = make_dto(
        name="   Garantie     Premium    Plus   "
    )

    # Act
    use_case.execute(dto)

    # Assert
    repository.find_by_name.assert_called_once_with(
        "Garantie Premium Plus"
    )

    plan = repository.save.call_args.args[0]

    assert plan.name == "Garantie Premium Plus"


def test_create_warranty_plan_rejects_duplicate_name():
    # Arrange
    (
        use_case,
        repository,
        event_service,
        unit_of_work,
    ) = make_use_case()

    existing_plan = Mock()
    repository.find_by_name.return_value = existing_plan

    dto = make_dto()

    # Act / Assert
    with pytest.raises(WarrantyPlanAlreadyExists):
        use_case.execute(dto)

    repository.find_by_name.assert_called_once_with(
        "Garantie Premium"
    )

    repository.find_by_plan_type.assert_not_called()
    repository.save.assert_not_called()
    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_create_warranty_plan_rejects_duplicate_type():
    # Arrange
    (
        use_case,
        repository,
        event_service,
        unit_of_work,
    ) = make_use_case()

    repository.find_by_name.return_value = None
    repository.find_by_plan_type.return_value = Mock()

    dto = make_dto()

    # Act / Assert
    with pytest.raises(WarrantyPlanAlreadyExists):
        use_case.execute(dto)

    repository.find_by_name.assert_called_once_with(
        "Garantie Premium"
    )

    repository.find_by_plan_type.assert_called_once_with(
        WarrantyPlanType.PREMIUM
    )

    repository.save.assert_not_called()
    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_create_warranty_plan_logs_creation_event():
    # Arrange
    (
        use_case,
        repository,
        event_service,
        unit_of_work,
    ) = make_use_case()

    repository.find_by_name.return_value = None
    repository.find_by_plan_type.return_value = None

    dto = make_dto()

    # Act
    result = use_case.execute(dto)

    # Assert
    event_service.log.assert_called_once()

    call = event_service.log.call_args

    assert call.kwargs["user_id"] == "admin-123"

    metadata = call.kwargs["event_metadata"]

    assert metadata["plan_id"] == result.plan_id
    assert metadata["name"] == "Garantie Premium"
    assert metadata["plan_type"] == WarrantyPlanType.PREMIUM.value
    assert metadata["duration_months"] == 24
    assert metadata["mileage_limit"] == 50000
    assert metadata["price"] == 1299.99
    assert metadata["active"] is True


def test_create_warranty_plan_rolls_back_when_save_fails():
    # Arrange
    (
        use_case,
        repository,
        event_service,
        unit_of_work,
    ) = make_use_case()

    repository.find_by_name.return_value = None
    repository.find_by_plan_type.return_value = None

    repository.save.side_effect = RuntimeError(
        "Database error"
    )

    dto = make_dto()

    # Act / Assert
    with pytest.raises(RuntimeError):
        use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()