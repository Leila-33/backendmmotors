from unittest.mock import Mock

import pytest

from modules.warranties.application.dtos.admin.toggle_warranty_plan_dto import (
    ToggleWarrantyPlanDTO,
)
from modules.warranties.application.use_cases.admin.toggle_warranty_plan import (
    ToggleWarrantyPlanUseCase,
)
from modules.warranties.domain.entities.warranty_plan import WarrantyPlan
from modules.warranties.domain.enums import WarrantyPlanType
from modules.warranties.domain.exceptions import (
    WarrantyPlanNotFound,
)
from modules.applications.domain.enums import EventType


def create_warranty_plan(active: bool) -> WarrantyPlan:
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
        active=active,
    )


def test_toggle_warranty_plan_activate():
    repository = Mock()
    event_service = Mock()
    unit_of_work = Mock()

    plan = create_warranty_plan(active=False)

    repository.get_by_id.return_value = plan

    dto = ToggleWarrantyPlanDTO(
        plan_id="plan-123",
        active=True,
        admin_id="admin-123",
    )

    use_case = ToggleWarrantyPlanUseCase(
        repository=repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )

    result = use_case.execute(dto)

    assert result is plan
    assert plan.active is True

    repository.get_by_id.assert_called_once_with("plan-123")
    repository.update.assert_called_once_with(plan)

    event_service.log.assert_called_once()

    event = event_service.log.call_args.kwargs

    assert event["type"] == EventType.WARRANTY_PLAN_ACTIVATED
    assert event["message"] == "Plan de garantie activé"
    assert event["user_id"] == "admin-123"

    assert event["event_metadata"]["plan_id"] == "plan-123"
    assert event["event_metadata"]["name"] == "Garantie Premium"
    assert event["event_metadata"]["old_status"] is False
    assert event["event_metadata"]["new_status"] is True

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


def test_toggle_warranty_plan_deactivate():
    repository = Mock()
    event_service = Mock()
    unit_of_work = Mock()

    plan = create_warranty_plan(active=True)

    repository.get_by_id.return_value = plan

    dto = ToggleWarrantyPlanDTO(
        plan_id="plan-123",
        active=False,
        admin_id="admin-123",
    )

    use_case = ToggleWarrantyPlanUseCase(
        repository=repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )

    result = use_case.execute(dto)

    assert result is plan
    assert plan.active is False

    repository.get_by_id.assert_called_once_with("plan-123")
    repository.update.assert_called_once_with(plan)

    event_service.log.assert_called_once()

    event = event_service.log.call_args.kwargs

    assert event["type"] == EventType.WARRANTY_PLAN_DEACTIVATED
    assert event["message"] == "Plan de garantie désactivé"
    assert event["user_id"] == "admin-123"

    assert event["event_metadata"]["plan_id"] == "plan-123"
    assert event["event_metadata"]["name"] == "Garantie Premium"
    assert event["event_metadata"]["old_status"] is True
    assert event["event_metadata"]["new_status"] is False

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


def test_toggle_warranty_plan_not_found():
    repository = Mock()
    event_service = Mock()
    unit_of_work = Mock()

    repository.get_by_id.return_value = None

    dto = ToggleWarrantyPlanDTO(
        plan_id="plan-123",
        active=True,
        admin_id="admin-123",
    )

    use_case = ToggleWarrantyPlanUseCase(
        repository=repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )

    with pytest.raises(WarrantyPlanNotFound):
        use_case.execute(dto)

    repository.get_by_id.assert_called_once_with("plan-123")

    repository.update.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_toggle_warranty_plan_rollback_when_update_fails():
    repository = Mock()
    event_service = Mock()
    unit_of_work = Mock()

    plan = create_warranty_plan(active=False)

    repository.get_by_id.return_value = plan

    repository.update.side_effect = RuntimeError("Database error")

    dto = ToggleWarrantyPlanDTO(
        plan_id="plan-123",
        active=True,
        admin_id="admin-123",
    )

    use_case = ToggleWarrantyPlanUseCase(
        repository=repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )

    with pytest.raises(RuntimeError, match="Database error"):
        use_case.execute(dto)

    repository.get_by_id.assert_called_once_with("plan-123")
    repository.update.assert_called_once_with(plan)

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()