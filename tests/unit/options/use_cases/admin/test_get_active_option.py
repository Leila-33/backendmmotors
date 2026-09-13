from unittest.mock import Mock

import pytest

from modules.options.application.results.admin.get_active_options_result import (
    GetActiveOptionsResult,
)
from modules.options.application.use_cases.admin.get_active_options import (
    GetActiveOptionsUseCase,
)


@pytest.fixture
def option_repository():
    return Mock()


@pytest.fixture
def use_case(option_repository):
    return GetActiveOptionsUseCase(
        option_repository=option_repository,
    )


def test_get_active_options_returns_options(
    use_case,
    option_repository,
):
    options = [
        Mock(id="option-1", name="GPS"),
        Mock(id="option-2", name="Climatisation"),
    ]

    option_repository.get_active.return_value = options

    result = use_case.execute()

    option_repository.get_active.assert_called_once_with()

    assert isinstance(result, GetActiveOptionsResult)
    assert result.options == options


def test_get_active_options_returns_empty_list(
    use_case,
    option_repository,
):
    option_repository.get_active.return_value = []

    result = use_case.execute()

    option_repository.get_active.assert_called_once_with()

    assert isinstance(result, GetActiveOptionsResult)
    assert result.options == []


def test_get_active_options_propagates_repository_error(
    use_case,
    option_repository,
):
    option_repository.get_active.side_effect = RuntimeError(
        "Database error"
    )

    with pytest.raises(
        RuntimeError,
        match="Database error",
    ):
        use_case.execute()

    option_repository.get_active.assert_called_once_with()