from unittest.mock import Mock

import pytest

from modules.options.application.results.admin.get_options_result import (
    GetOptionsResult,
)
from modules.options.application.use_cases.admin.get_options import (
    GetOptionsUseCase,
)


@pytest.fixture
def option_repository():
    return Mock()


@pytest.fixture
def use_case(option_repository):
    return GetOptionsUseCase(
        option_repository=option_repository,
    )


def test_get_options_returns_all_options(
    use_case,
    option_repository,
):
    options = [
        Mock(id="option-1", name="GPS"),
        Mock(id="option-2", name="Climatisation"),
    ]

    option_repository.get_all.return_value = options

    result = use_case.execute()

    option_repository.get_all.assert_called_once_with()

    assert isinstance(result, GetOptionsResult)
    assert result.options == options


def test_get_options_returns_empty_list(
    use_case,
    option_repository,
):
    option_repository.get_all.return_value = []

    result = use_case.execute()

    option_repository.get_all.assert_called_once_with()

    assert isinstance(result, GetOptionsResult)
    assert result.options == []


def test_get_options_propagates_repository_error(
    use_case,
    option_repository,
):
    option_repository.get_all.side_effect = RuntimeError(
        "Database error"
    )

    with pytest.raises(
        RuntimeError,
        match="Database error",
    ):
        use_case.execute()

    option_repository.get_all.assert_called_once_with()