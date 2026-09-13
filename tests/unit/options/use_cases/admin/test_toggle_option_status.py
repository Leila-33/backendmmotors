from unittest.mock import Mock

import pytest

from modules.applications.domain.enums import EventType
from modules.options.domain.exceptions import OptionNotFound

from modules.options.application.dtos.admin.toggle_option_status_dto import (
    ToggleOptionStatusDTO,
)
from modules.options.application.results.admin.toggle_option_status_result import (
    ToggleOptionStatusResult,
)
from modules.options.application.use_cases.admin.toggle_option_status import (
    ToggleOptionStatusUseCase,
)


@pytest.fixture
def option_repository():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    option_repository,
    event_service,
    unit_of_work,
):
    return ToggleOptionStatusUseCase(
        option_repository=option_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


def make_dto(
    option_id="option-123",
    admin_id="admin-123",
    is_active=True,
):
    return ToggleOptionStatusDTO(
        option_id=option_id,
        admin_id=admin_id,
        is_active=is_active,
    )


def make_option(
    option_id="option-123",
    is_active=True,
):
    option = Mock()
    option.id = option_id
    option.is_active = is_active
    return option


def test_toggle_option_status_activates_option(
    use_case,
    option_repository,
    event_service,
    unit_of_work,
):
    option = make_option(is_active=False)
    dto = make_dto(is_active=True)

    option_repository.get_by_id.return_value = option

    result = use_case.execute(dto)

    assert option.is_active is True

    option_repository.get_by_id.assert_called_once_with(
        "option-123"
    )

    option_repository.update.assert_called_once_with(
        option
    )

    event_service.log.assert_called_once_with(
        type=EventType.OPTION_ACTIVATED,
        message="Option activée",
        user_id="admin-123",
        event_metadata={
            "option_id": "option-123",
            "old_status": False,
            "new_status": True,
        },
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()

    assert isinstance(result, ToggleOptionStatusResult)
    assert result.id == "option-123"
    assert result.is_active is True
    assert result.message == "Option activée"


def test_toggle_option_status_deactivates_option(
    use_case,
    option_repository,
    event_service,
    unit_of_work,
):
    option = make_option(is_active=True)
    dto = make_dto(is_active=False)

    option_repository.get_by_id.return_value = option

    result = use_case.execute(dto)

    assert option.is_active is False

    option_repository.get_by_id.assert_called_once_with(
        "option-123"
    )

    option_repository.update.assert_called_once_with(
        option
    )

    event_service.log.assert_called_once_with(
        type=EventType.OPTION_DEACTIVATED,
        message="Option désactivée",
        user_id="admin-123",
        event_metadata={
            "option_id": "option-123",
            "old_status": True,
            "new_status": False,
        },
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()

    assert isinstance(result, ToggleOptionStatusResult)
    assert result.id == "option-123"
    assert result.is_active is False
    assert result.message == "Option désactivée"


def test_toggle_option_status_raises_when_option_not_found(
    use_case,
    option_repository,
    event_service,
    unit_of_work,
):
    dto = make_dto()

    option_repository.get_by_id.return_value = None

    with pytest.raises(OptionNotFound):
        use_case.execute(dto)

    option_repository.get_by_id.assert_called_once_with(
        "option-123"
    )

    option_repository.update.assert_not_called()
    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_toggle_option_status_rolls_back_when_update_fails(
    use_case,
    option_repository,
    event_service,
    unit_of_work,
):
    option = make_option(is_active=False)
    dto = make_dto(is_active=True)

    option_repository.get_by_id.return_value = option
    option_repository.update.side_effect = RuntimeError(
        "Database error"
    )

    with pytest.raises(
        RuntimeError,
        match="Database error",
    ):
        use_case.execute(dto)

    assert option.is_active is True

    option_repository.update.assert_called_once_with(
        option
    )

    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_toggle_option_status_rolls_back_when_event_fails(
    use_case,
    option_repository,
    event_service,
    unit_of_work,
):
    option = make_option(is_active=True)
    dto = make_dto(is_active=False)

    option_repository.get_by_id.return_value = option
    event_service.log.side_effect = RuntimeError(
        "Event error"
    )

    with pytest.raises(
        RuntimeError,
        match="Event error",
    ):
        use_case.execute(dto)

    assert option.is_active is False

    option_repository.update.assert_called_once_with(
        option
    )

    event_service.log.assert_called_once()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_toggle_option_status_rolls_back_when_commit_fails(
    use_case,
    option_repository,
    event_service,
    unit_of_work,
):
    option = make_option(is_active=False)
    dto = make_dto(is_active=True)

    option_repository.get_by_id.return_value = option
    unit_of_work.commit.side_effect = RuntimeError(
        "Commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="Commit error",
    ):
        use_case.execute(dto)

    assert option.is_active is True

    option_repository.update.assert_called_once_with(
        option
    )

    event_service.log.assert_called_once()
    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()