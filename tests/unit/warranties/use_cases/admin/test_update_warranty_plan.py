from unittest.mock import Mock

import pytest

from modules.warranties.application.dtos.admin.update_warranty_plan_dto import (
    UpdateWarrantyPlanDTO,
)
from modules.warranties.application.use_cases.admin.update_warranty_plan import (
    UpdateWarrantyPlanUseCase,
)
from modules.warranties.domain.entities.warranty_plan import WarrantyPlan
from modules.warranties.domain.enums import WarrantyPlanType
from modules.warranties.domain.exceptions import (
    WarrantyPlanAlreadyExists,
    WarrantyPlanNotFound,
)
from modules.applications.domain.enums import EventType


def create_warranty_plan() -> WarrantyPlan:
    return WarrantyPlan(
        id="plan-123",
        name="Garantie Premium",
        description="Garantie complète",
        plan_type=WarrantyPlanType.PREMIUM,
        duration_months=12,
        mileage_limit=20000,
        covers_engine=True,
        covers_transmission=True,
        covers_electronics=True,
        covers_assistance=True,
        covers_wear_parts=False,
        price=500.0,
        active=True,
    )


def create_update_dto() -> UpdateWarrantyPlanDTO:
    return UpdateWarrantyPlanDTO(
        plan_id="plan-123",
        name="Garantie Premium Plus",
        description="Garantie complète étendue",
        plan_type=WarrantyPlanType.PREMIUM,
        duration_months=24,
        mileage_limit=40000,
        covers_engine=True,
        covers_transmission=True,
        covers_electronics=True,
        covers_assistance=True,
        covers_wear_parts=True,
        price=700.0,
        admin_id="admin-123",
    )


def test_update_warranty_plan_success():
    repository = Mock()
    event_service = Mock()
    unit_of_work = Mock()

    plan = create_warranty_plan()
    dto = create_update_dto()

    repository.get_by_id.return_value = plan
    repository.find_by_name.return_value = None
    repository.find_by_plan_type.return_value = None

    use_case = UpdateWarrantyPlanUseCase(
        repository=repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )

    result = use_case.execute(dto)

    assert result is plan

    assert plan.name == "Garantie Premium Plus"
    assert plan.description == "Garantie complète étendue"
    assert plan.plan_type == WarrantyPlanType.PREMIUM
    assert plan.duration_months == 24
    assert plan.mileage_limit == 40000
    assert plan.covers_engine is True
    assert plan.covers_transmission is True
    assert plan.covers_electronics is True
    assert plan.covers_assistance is True
    assert plan.covers_wear_parts is True
    assert plan.price == 700.0

    repository.get_by_id.assert_called_once_with("plan-123")
    repository.find_by_name.assert_called_once_with(
        "Garantie Premium Plus"
    )
    repository.find_by_plan_type.assert_called_once_with(
        WarrantyPlanType.PREMIUM
    )
    repository.update.assert_called_once_with(plan)

    event_service.log.assert_called_once()

    event = event_service.log.call_args.kwargs

    assert event["type"] == EventType.WARRANTY_PLAN_UPDATED
    assert event["message"] == "Plan de garantie modifié"
    assert event["user_id"] == "admin-123"

    assert event["event_metadata"]["plan_id"] == "plan-123"

    assert set(event["event_metadata"]["updated_fields"]) == {
        "name",
        "description",
        "duration_months",
        "mileage_limit",
        "covers_wear_parts",
        "price",
    }

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


def test_update_warranty_plan_normalizes_name():
    repository = Mock()
    event_service = Mock()
    unit_of_work = Mock()

    plan = create_warranty_plan()

    dto = UpdateWarrantyPlanDTO(
        plan_id="plan-123",
        name="   Garantie    Premium    Plus   ",
        description="Garantie complète",
        plan_type=WarrantyPlanType.PREMIUM,
        duration_months=12,
        mileage_limit=20000,
        covers_engine=True,
        covers_transmission=True,
        covers_electronics=True,
        covers_assistance=True,
        covers_wear_parts=False,
        price=500.0,
        admin_id="admin-123",
    )

    repository.get_by_id.return_value = plan
    repository.find_by_name.return_value = None
    repository.find_by_plan_type.return_value = None

    use_case = UpdateWarrantyPlanUseCase(
        repository=repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )

    result = use_case.execute(dto)

    assert result is plan
    assert plan.name == "Garantie Premium Plus"

    repository.find_by_name.assert_called_once_with(
        "Garantie Premium Plus"
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


def test_update_warranty_plan_not_found():
    repository = Mock()
    event_service = Mock()
    unit_of_work = Mock()

    repository.get_by_id.return_value = None

    dto = create_update_dto()

    use_case = UpdateWarrantyPlanUseCase(
        repository=repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )

    with pytest.raises(WarrantyPlanNotFound):
        use_case.execute(dto)

    repository.get_by_id.assert_called_once_with("plan-123")

    repository.find_by_name.assert_not_called()
    repository.find_by_plan_type.assert_not_called()
    repository.update.assert_not_called()

    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_update_warranty_plan_name_already_exists():
    repository = Mock()
    event_service = Mock()
    unit_of_work = Mock()

    plan = create_warranty_plan()

    other_plan = WarrantyPlan(
        id="plan-456",
        name="Garantie Premium Plus",
        description="Autre garantie",
        plan_type=WarrantyPlanType.PREMIUM,
        duration_months=24,
        mileage_limit=40000,
        covers_engine=True,
        covers_transmission=True,
        covers_electronics=True,
        covers_assistance=True,
        covers_wear_parts=True,
        price=700.0,
        active=True,
    )

    repository.get_by_id.return_value = plan
    repository.find_by_name.return_value = other_plan

    dto = create_update_dto()

    use_case = UpdateWarrantyPlanUseCase(
        repository=repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )

    with pytest.raises(
        WarrantyPlanAlreadyExists,
        match="Plan déjà existant",
    ):
        use_case.execute(dto)

    repository.get_by_id.assert_called_once_with("plan-123")
    repository.find_by_name.assert_called_once_with(
        "Garantie Premium Plus"
    )

    repository.find_by_plan_type.assert_not_called()
    repository.update.assert_not_called()

    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_update_warranty_plan_rollback_when_update_fails():
    repository = Mock()
    event_service = Mock()
    unit_of_work = Mock()

    plan = create_warranty_plan()
    dto = create_update_dto()

    repository.get_by_id.return_value = plan
    repository.find_by_name.return_value = None
    repository.find_by_plan_type.return_value = None

    repository.update.side_effect = RuntimeError(
        "Database error"
    )

    use_case = UpdateWarrantyPlanUseCase(
        repository=repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )

    with pytest.raises(
        RuntimeError,
        match="Database error",
    ):
        use_case.execute(dto)

    repository.get_by_id.assert_called_once_with("plan-123")
    repository.update.assert_called_once_with(plan)

    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()