from unittest.mock import Mock

from modules.warranties.application.use_cases.admin.get_warranty_plans import (
    GetWarrantyPlansUseCase,
)


def test_get_warranty_plans_returns_repository_result():
    repository = Mock()

    expected_plans = [
        Mock(id="1", name="Essentiel"),
        Mock(id="2", name="Premium"),
    ]

    repository.find_all.return_value = expected_plans

    use_case = GetWarrantyPlansUseCase(repository)

    result = use_case.execute()

    assert result == expected_plans
    repository.find_all.assert_called_once_with()