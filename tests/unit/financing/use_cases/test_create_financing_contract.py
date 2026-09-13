from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from modules.applications.domain.enums import EventType
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.financing.application.dtos.create_financing_contract_dto import (
    CreateFinancingContractDTO,
)
from modules.financing.application.results.create_financing_contract_result import (
    CreateFinancingContractResult,
)
from modules.financing.application.use_cases.create_financing_contract import (
    CreateFinancingContractUseCase,
)
from modules.financing.domain.exceptions import FinancingDataNotFound
from modules.financing.domain.entities.financing_contract import (
    FinancingContract,
)


@pytest.fixture
def application_repository():
    return Mock()


@pytest.fixture
def financing_contract_repository():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def use_case(
    application_repository,
    financing_contract_repository,
    event_service,
):
    return CreateFinancingContractUseCase(
        application_repository=application_repository,
        financing_contract_repository=financing_contract_repository,
        event_service=event_service,
    )


@pytest.fixture
def dto():
    return CreateFinancingContractDTO(
        application_id="application-123",
    )


@pytest.fixture
def financing():
    return SimpleNamespace(
        financed_amount=20000.0,
        monthly_payment=350.0,
        duration_months=60,
    )


@pytest.fixture
def application(financing):
    return SimpleNamespace(
        id="application-123",
        user_id="user-123",
        vehicle_id="vehicle-123",
        financing=financing,
    )


def test_execute_raises_when_application_does_not_exist(
    use_case,
    application_repository,
    financing_contract_repository,
    event_service,
    dto,
):
    application_repository.get_by_id.return_value = None

    with pytest.raises(ApplicationNotFound):
        use_case.execute(dto)

    application_repository.get_by_id.assert_called_once_with(
        dto.application_id
    )

    financing_contract_repository.find_by_application_id.assert_not_called()
    financing_contract_repository.save.assert_not_called()
    event_service.log.assert_not_called()


def test_execute_raises_when_financing_data_does_not_exist(
    use_case,
    application_repository,
    financing_contract_repository,
    event_service,
    dto,
):
    application = SimpleNamespace(
        id="application-123",
        user_id="user-123",
        vehicle_id="vehicle-123",
        financing=None,
    )

    application_repository.get_by_id.return_value = application

    with pytest.raises(FinancingDataNotFound):
        use_case.execute(dto)

    financing_contract_repository.find_by_application_id.assert_not_called()
    financing_contract_repository.save.assert_not_called()
    event_service.log.assert_not_called()


@pytest.mark.parametrize(
    "financed_amount",
    [0, -1, -5000],
)
def test_execute_raises_when_financed_amount_is_not_positive(
    use_case,
    application_repository,
    financing_contract_repository,
    event_service,
    dto,
    financed_amount,
):
    application = SimpleNamespace(
        id="application-123",
        user_id="user-123",
        vehicle_id="vehicle-123",
        financing=SimpleNamespace(
            financed_amount=financed_amount,
            monthly_payment=350.0,
            duration_months=60,
        ),
    )

    application_repository.get_by_id.return_value = application

    with pytest.raises(FinancingDataNotFound):
        use_case.execute(dto)

    financing_contract_repository.find_by_application_id.assert_not_called()
    financing_contract_repository.save.assert_not_called()
    event_service.log.assert_not_called()


def test_execute_returns_existing_contract_without_creating_another(
    use_case,
    application_repository,
    financing_contract_repository,
    event_service,
    dto,
    application,
):
    existing_contract = SimpleNamespace(
        id="contract-123",
        application_id="application-123",
        financed_amount=20000.0,
        monthly_payment=350.0,
        duration_months=60,
        remaining_balance=20000.0,
    )

    application_repository.get_by_id.return_value = application
    financing_contract_repository.find_by_application_id.return_value = (
        existing_contract
    )

    result = use_case.execute(dto)

    financing_contract_repository.find_by_application_id.assert_called_once_with(
        dto.application_id
    )

    financing_contract_repository.save.assert_not_called()
    event_service.log.assert_not_called()

    assert isinstance(result, CreateFinancingContractResult)
    assert result.contract_id == "contract-123"
    assert result.application_id == "application-123"
    assert result.financed_amount == 20000.0
    assert result.monthly_payment == 350.0
    assert result.duration_months == 60
    assert result.remaining_balance == 20000.0


def test_execute_creates_financing_contract_successfully(
    use_case,
    application_repository,
    financing_contract_repository,
    event_service,
    dto,
    application,
):
    application_repository.get_by_id.return_value = application
    financing_contract_repository.find_by_application_id.return_value = None

    saved_contract = SimpleNamespace(
        id="contract-123",
        application_id="application-123",
        financed_amount=20000.0,
        monthly_payment=350.0,
        duration_months=60,
        remaining_balance=20000.0,
    )

    financing_contract_repository.save.return_value = saved_contract

    result = use_case.execute(dto)

    application_repository.get_by_id.assert_called_once_with(
        dto.application_id
    )

    financing_contract_repository.find_by_application_id.assert_called_once_with(
        dto.application_id
    )

    financing_contract_repository.save.assert_called_once()

    contract_arg = financing_contract_repository.save.call_args.args[0]

    assert isinstance(contract_arg, FinancingContract)
    assert contract_arg.application_id == application.id
    assert contract_arg.financed_amount == 20000.0
    assert contract_arg.monthly_payment == 350.0
    assert contract_arg.duration_months == 60
    assert contract_arg.remaining_balance == 20000.0
    assert contract_arg.id
    assert contract_arg.created_at is not None
    assert contract_arg.created_at.tzinfo is not None

    assert isinstance(result, CreateFinancingContractResult)
    assert result.contract_id == "contract-123"
    assert result.application_id == "application-123"
    assert result.financed_amount == 20000.0
    assert result.monthly_payment == 350.0
    assert result.duration_months == 60
    assert result.remaining_balance == 20000.0


def test_execute_logs_financing_contract_created_event(
    use_case,
    application_repository,
    financing_contract_repository,
    event_service,
    dto,
    application,
):
    application_repository.get_by_id.return_value = application
    financing_contract_repository.find_by_application_id.return_value = None

    saved_contract = SimpleNamespace(
        id="contract-123",
        application_id="application-123",
        financed_amount=20000.0,
        monthly_payment=350.0,
        duration_months=60,
        remaining_balance=20000.0,
    )

    financing_contract_repository.save.return_value = saved_contract

    use_case.execute(dto)

    event_service.log.assert_called_once_with(
        application_id=application.id,
        vehicle_id=application.vehicle_id,
        user_id=application.user_id,
        type=EventType.FINANCING_CONTRACT_CREATED,
        message="Contrat de financement créé.",
        event_metadata={
            "contract_id": saved_contract.id,
            "financed_amount": saved_contract.financed_amount,
        },
    )


def test_execute_propagates_repository_save_error(
    use_case,
    application_repository,
    financing_contract_repository,
    event_service,
    dto,
    application,
):
    application_repository.get_by_id.return_value = application
    financing_contract_repository.find_by_application_id.return_value = None
    financing_contract_repository.save.side_effect = RuntimeError(
        "Database error"
    )

    with pytest.raises(
        RuntimeError,
        match="Database error",
    ):
        use_case.execute(dto)

    financing_contract_repository.save.assert_called_once()
    event_service.log.assert_not_called()