from unittest.mock import Mock, patch

import pytest

from modules.applications.domain.enums import EventType
from modules.options.domain.enums import OptionType
from modules.options.domain.exceptions import OptionAlreadyExists

from modules.options.application.dtos.admin.create_option_dto import (
    CreateOptionDTO,
)
from modules.options.application.use_cases.admin.create_option import (
    CreateOptionUseCase,
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
    return CreateOptionUseCase(
        option_repository=option_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


@pytest.fixture
def dto():
    return CreateOptionDTO(
        admin_id="admin-123",
        name="  GPS  ",
        price=250.00,
        billing_type="ONE_TIME",
    )


def test_create_option_success(
    use_case,
    option_repository,
    event_service,
    unit_of_work,
    dto,
):
    saved_option = Mock()
    saved_option.id = "option-123"
    saved_option.name = "GPS"

    option_repository.exists_by_name.return_value = False
    option_repository.save.return_value = saved_option

    with patch(
        "modules.options.application.use_cases.admin.create_option.uuid4",
        return_value="option-123",
    ):
        result = use_case.execute(dto)

    option_repository.exists_by_name.assert_called_once_with(
        "GPS"
    )

    option_repository.save.assert_called_once()

    option = option_repository.save.call_args.args[0]

    assert option.id == "option-123"
    assert option.name == "GPS"
    assert option.type == OptionType.CUSTOM
    assert option.price == 250.00
    assert option.billing_type == "ONE_TIME"
    assert option.is_active is True

    event_service.log.assert_called_once_with(
        type=EventType.OPTION_CREATED,
        message="Option créée",
        user_id="admin-123",
        event_metadata={
            "option_id": "option-123",
            "name": "GPS",
        },
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()

    assert result.option_id == "option-123"
    assert result.message == "Option créée avec succès"


def test_create_option_normalizes_name(
    use_case,
    option_repository,
    dto,
):
    saved_option = Mock()
    saved_option.id = "option-123"
    saved_option.name = "GPS"

    option_repository.exists_by_name.return_value = False
    option_repository.save.return_value = saved_option

    with patch(
        "modules.options.application.use_cases.admin.create_option.uuid4",
        return_value="option-123",
    ):
        use_case.execute(dto)

    option_repository.exists_by_name.assert_called_once_with(
        "GPS"
    )

    option = option_repository.save.call_args.args[0]

    assert option.name == "GPS"


def test_create_option_raises_when_name_already_exists(
    use_case,
    option_repository,
    event_service,
    unit_of_work,
    dto,
):
    option_repository.exists_by_name.return_value = True

    with pytest.raises(OptionAlreadyExists):
        use_case.execute(dto)

    option_repository.exists_by_name.assert_called_once_with(
        "GPS"
    )

    option_repository.save.assert_not_called()
    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_create_option_rolls_back_when_save_fails(
    use_case,
    option_repository,
    event_service,
    unit_of_work,
    dto,
):
    option_repository.exists_by_name.return_value = False
    option_repository.save.side_effect = RuntimeError(
        "Database error"
    )

    with pytest.raises(
        RuntimeError,
        match="Database error",
    ):
        use_case.execute(dto)

    option_repository.save.assert_called_once()

    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_create_option_rolls_back_when_event_fails(
    use_case,
    option_repository,
    event_service,
    unit_of_work,
    dto,
):
    saved_option = Mock()
    saved_option.id = "option-123"
    saved_option.name = "GPS"

    option_repository.exists_by_name.return_value = False
    option_repository.save.return_value = saved_option

    event_service.log.side_effect = RuntimeError(
        "Event error"
    )

    with patch(
        "modules.options.application.use_cases.admin.create_option.uuid4",
        return_value="option-123",
    ):
        with pytest.raises(
            RuntimeError,
            match="Event error",
        ):
            use_case.execute(dto)

    option_repository.save.assert_called_once()
    event_service.log.assert_called_once()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_create_option_rolls_back_when_commit_fails(
    use_case,
    option_repository,
    event_service,
    unit_of_work,
    dto,
):
    saved_option = Mock()
    saved_option.id = "option-123"
    saved_option.name = "GPS"

    option_repository.exists_by_name.return_value = False
    option_repository.save.return_value = saved_option

    unit_of_work.commit.side_effect = RuntimeError(
        "Commit error"
    )

    with patch(
        "modules.options.application.use_cases.admin.create_option.uuid4",
        return_value="option-123",
    ):
        with pytest.raises(
            RuntimeError,
            match="Commit error",
        ):
            use_case.execute(dto)

    option_repository.save.assert_called_once()
    event_service.log.assert_called_once()
    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


def test_create_option_propagates_repository_exists_error(
    use_case,
    option_repository,
    event_service,
    unit_of_work,
    dto,
):
    option_repository.exists_by_name.side_effect = RuntimeError(
        "Database error"
    )

    with pytest.raises(
        RuntimeError,
        match="Database error",
    ):
        use_case.execute(dto)

    option_repository.save.assert_not_called()
    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()
