from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from modules.financing.application.dtos.create_installments_dto import (
    CreateInstallmentsDTO,
)
from modules.financing.application.results.create_installments_result import (
    CreateInstallmentsResult,
)
from modules.financing.application.use_cases.create_installments import (
    CreateInstallmentsUseCase,
)
from modules.financing.domain.entities.installment import (
    InstallmentPayment,
)
from modules.financing.domain.enums import InstallmentStatus
from modules.financing.domain.exceptions import (
    FinancingContractNotFound,
)


@pytest.fixture
def financing_contract_repository():
    return Mock()


@pytest.fixture
def installment_repository():
    return Mock()


@pytest.fixture
def use_case(
    financing_contract_repository,
    installment_repository,
):
    return CreateInstallmentsUseCase(
        financing_contract_repository=financing_contract_repository,
        installment_repository=installment_repository,
    )


@pytest.fixture
def dto():
    return CreateInstallmentsDTO(
        contract_id="contract-123",
    )


@pytest.fixture
def contract():
    return SimpleNamespace(
        id="contract-123",
        duration_months=12,
        monthly_payment=350.0,
        created_at=datetime(
            2026,
            1,
            15,
            10,
            30,
            tzinfo=timezone.utc,
        ),
    )


def test_execute_raises_when_contract_does_not_exist(
    use_case,
    financing_contract_repository,
    installment_repository,
    dto,
):
    financing_contract_repository.find_by_id.return_value = None

    with pytest.raises(FinancingContractNotFound):
        use_case.execute(dto)

    financing_contract_repository.find_by_id.assert_called_once_with(
        dto.contract_id
    )

    installment_repository.count_by_contract_id.assert_not_called()
    installment_repository.find_all_by_contract_id.assert_not_called()
    installment_repository.save_all.assert_not_called()


def test_execute_returns_existing_installments_without_creating_new_ones(
    use_case,
    financing_contract_repository,
    installment_repository,
    dto,
    contract,
):
    financing_contract_repository.find_by_id.return_value = contract

    installment_repository.count_by_contract_id.return_value = 3

    existing_installments = [
        SimpleNamespace(id="installment-1"),
        SimpleNamespace(id="installment-2"),
        SimpleNamespace(id="installment-3"),
    ]

    installment_repository.find_all_by_contract_id.return_value = (
        existing_installments
    )

    result = use_case.execute(dto)

    financing_contract_repository.find_by_id.assert_called_once_with(
        dto.contract_id
    )

    installment_repository.count_by_contract_id.assert_called_once_with(
        contract.id
    )

    installment_repository.find_all_by_contract_id.assert_called_once_with(
        contract.id
    )

    installment_repository.save_all.assert_not_called()

    assert isinstance(result, CreateInstallmentsResult)
    assert result.contract_id == contract.id
    assert result.installment_ids == [
        "installment-1",
        "installment-2",
        "installment-3",
    ]
    assert result.count == 3


def test_execute_creates_all_installments(
    use_case,
    financing_contract_repository,
    installment_repository,
    dto,
    contract,
):
    financing_contract_repository.find_by_id.return_value = contract

    installment_repository.count_by_contract_id.return_value = 0

    saved_installments = [
        SimpleNamespace(id="installment-1"),
        SimpleNamespace(id="installment-2"),
        SimpleNamespace(id="installment-3"),
        SimpleNamespace(id="installment-4"),
    ]

    installment_repository.save_all.return_value = saved_installments

    contract.duration_months = 4

    result = use_case.execute(dto)

    financing_contract_repository.find_by_id.assert_called_once_with(
        dto.contract_id
    )

    installment_repository.count_by_contract_id.assert_called_once_with(
        contract.id
    )

    installment_repository.find_all_by_contract_id.assert_not_called()

    installment_repository.save_all.assert_called_once()

    installments_arg = (
        installment_repository.save_all.call_args.args[0]
    )

    assert len(installments_arg) == 4

    for index, installment in enumerate(
        installments_arg,
        start=1,
    ):
        assert isinstance(
            installment,
            InstallmentPayment,
        )

        assert installment.financing_contract_id == contract.id
        assert installment.installment_number == index
        assert installment.amount == 350.0
        assert installment.status == InstallmentStatus.PENDING

        assert installment.id
        assert installment.due_date is not None

    assert installments_arg[0].due_date == (
        datetime(
            2026,
            2,
            15,
            10,
            30,
            tzinfo=timezone.utc,
        )
    )

    assert installments_arg[1].due_date == (
        datetime(
            2026,
            3,
            15,
            10,
            30,
            tzinfo=timezone.utc,
        )
    )

    assert installments_arg[2].due_date == (
        datetime(
            2026,
            4,
            15,
            10,
            30,
            tzinfo=timezone.utc,
        )
    )

    assert installments_arg[3].due_date == (
        datetime(
            2026,
            5,
            15,
            10,
            30,
            tzinfo=timezone.utc,
        )
    )

    assert isinstance(
        result,
        CreateInstallmentsResult,
    )

    assert result.contract_id == contract.id
    assert result.installment_ids == [
        "installment-1",
        "installment-2",
        "installment-3",
        "installment-4",
    ]
    assert result.count == 4


def test_execute_creates_one_installment_for_one_month_contract(
    use_case,
    financing_contract_repository,
    installment_repository,
    dto,
    contract,
):
    financing_contract_repository.find_by_id.return_value = contract
    installment_repository.count_by_contract_id.return_value = 0

    contract.duration_months = 1

    saved_installment = SimpleNamespace(
        id="installment-1",
    )

    installment_repository.save_all.return_value = [
        saved_installment
    ]

    result = use_case.execute(dto)

    installments_arg = (
        installment_repository.save_all.call_args.args[0]
    )

    assert len(installments_arg) == 1

    installment = installments_arg[0]

    assert installment.installment_number == 1
    assert installment.amount == contract.monthly_payment
    assert installment.status == InstallmentStatus.PENDING

    assert installment.due_date == datetime(
        2026,
        2,
        15,
        10,
        30,
        tzinfo=timezone.utc,
    )

    assert result.count == 1
    assert result.installment_ids == ["installment-1"]


def test_execute_propagates_save_all_error(
    use_case,
    financing_contract_repository,
    installment_repository,
    dto,
    contract,
):
    financing_contract_repository.find_by_id.return_value = contract
    installment_repository.count_by_contract_id.return_value = 0

    installment_repository.save_all.side_effect = RuntimeError(
        "Database error"
    )

    with pytest.raises(
        RuntimeError,
        match="Database error",
    ):
        use_case.execute(dto)

    installment_repository.save_all.assert_called_once()