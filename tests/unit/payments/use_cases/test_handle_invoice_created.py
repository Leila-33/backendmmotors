import pytest
from unittest.mock import Mock

from modules.financing.domain.exceptions import (
    FinancingContractNotFound,
)

from modules.payments.application.dtos.handle_invoice_created_dto import (
    HandleInvoiceCreatedDTO,
)

from modules.payments.application.results.handle_invoice_created_result import (
    HandleInvoiceCreatedResult,
)

from modules.payments.application.use_cases.handle_invoice_created import (
    HandleInvoiceCreatedUseCase,
)


@pytest.fixture
def financing_contract_repository():
    return Mock()


@pytest.fixture
def installment_repository():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    financing_contract_repository,
    installment_repository,
    unit_of_work,
):
    return HandleInvoiceCreatedUseCase(
        financing_contract_repository=financing_contract_repository,
        installment_repository=installment_repository,
        unit_of_work=unit_of_work,
    )


def make_dto(
    subscription_id="sub-123",
    invoice_id="invoice-123",
):
    return HandleInvoiceCreatedDTO(
        subscription_id=subscription_id,
        invoice_id=invoice_id,
    )


def make_contract(
    contract_id="contract-123",
):
    contract = Mock()

    contract.id = contract_id

    return contract


def make_installment(
    installment_id="installment-123",
    stripe_invoice_id=None,
):
    installment = Mock()

    installment.id = installment_id
    installment.stripe_invoice_id = stripe_invoice_id

    return installment


def test_execute_returns_none_when_subscription_id_is_missing(
    use_case,
    financing_contract_repository,
    installment_repository,
    unit_of_work,
):
    dto = make_dto(
        subscription_id=None,
    )

    result = use_case.execute(dto)

    assert result is None

    financing_contract_repository.get_by_subscription_id.assert_not_called()
    installment_repository.find_by_stripe_invoice_id.assert_not_called()
    installment_repository.find_next_unpaid.assert_not_called()
    installment_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_not_called()


def test_execute_returns_existing_installment_when_invoice_already_exists(
    use_case,
    financing_contract_repository,
    installment_repository,
    unit_of_work,
):
    existing_installment = make_installment(
        installment_id="installment-existing",
        stripe_invoice_id="invoice-123",
    )

    installment_repository.find_by_stripe_invoice_id.return_value = (
        existing_installment
    )

    dto = make_dto()

    result = use_case.execute(dto)

    assert isinstance(
        result,
        HandleInvoiceCreatedResult,
    )

    assert result.installment_id == "installment-existing"
    assert result.invoice_id == "invoice-123"
    assert result.message == "Facture déjà associée à une échéance"

    installment_repository.find_by_stripe_invoice_id.assert_called_once_with(
        "invoice-123"
    )

    # Très important : le contrat ne doit pas être recherché.
    financing_contract_repository.get_by_subscription_id.assert_not_called()

    installment_repository.find_next_unpaid.assert_not_called()
    installment_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_not_called()


def test_execute_raises_when_financing_contract_not_found(
    use_case,
    financing_contract_repository,
    installment_repository,
    unit_of_work,
):
    installment_repository.find_by_stripe_invoice_id.return_value = None
    financing_contract_repository.get_by_subscription_id.return_value = None

    dto = make_dto()

    with pytest.raises(FinancingContractNotFound):
        use_case.execute(dto)

    financing_contract_repository.get_by_subscription_id.assert_called_once_with(
        "sub-123"
    )

    installment_repository.find_next_unpaid.assert_not_called()
    installment_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_execute_returns_none_when_no_unpaid_installment_exists(
    use_case,
    financing_contract_repository,
    installment_repository,
    unit_of_work,
):
    contract = make_contract()

    installment_repository.find_by_stripe_invoice_id.return_value = None
    financing_contract_repository.get_by_subscription_id.return_value = (
        contract
    )
    installment_repository.find_next_unpaid.return_value = None

    dto = make_dto()

    result = use_case.execute(dto)

    assert result is None

    financing_contract_repository.get_by_subscription_id.assert_called_once_with(
        "sub-123"
    )

    installment_repository.find_next_unpaid.assert_called_once_with(
        "contract-123"
    )

    installment_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_not_called()


def test_execute_links_invoice_to_installment_successfully(
    use_case,
    financing_contract_repository,
    installment_repository,
    unit_of_work,
):
    contract = make_contract()

    installment = make_installment(
        installment_id="installment-123",
    )

    installment_repository.find_by_stripe_invoice_id.return_value = None
    financing_contract_repository.get_by_subscription_id.return_value = (
        contract
    )
    installment_repository.find_next_unpaid.return_value = installment

    dto = make_dto(
        invoice_id="invoice-456",
    )

    result = use_case.execute(dto)

    assert isinstance(
        result,
        HandleInvoiceCreatedResult,
    )

    assert result.installment_id == "installment-123"
    assert result.invoice_id == "invoice-456"
    assert result.message == (
        "Facture Stripe associée à l'échéance"
    )

    assert installment.stripe_invoice_id == "invoice-456"

    installment_repository.update.assert_called_once_with(
        installment
    )

    unit_of_work.commit.assert_called_once_with()
    unit_of_work.rollback.assert_not_called()


def test_execute_rolls_back_when_contract_repository_fails(
    use_case,
    financing_contract_repository,
    installment_repository,
    unit_of_work,
):
    installment_repository.find_by_stripe_invoice_id.return_value = None

    financing_contract_repository.get_by_subscription_id.side_effect = (
        RuntimeError("Database error")
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="Database error",
    ):
        use_case.execute(dto)

    installment_repository.find_by_stripe_invoice_id.assert_called_once_with(
        "invoice-123"
    )

    installment_repository.find_next_unpaid.assert_not_called()
    installment_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


def test_execute_rolls_back_when_installment_update_fails(
    use_case,
    financing_contract_repository,
    installment_repository,
    unit_of_work,
):
    contract = make_contract()

    installment = make_installment()

    installment_repository.find_by_stripe_invoice_id.return_value = None
    financing_contract_repository.get_by_subscription_id.return_value = (
        contract
    )
    installment_repository.find_next_unpaid.return_value = installment

    installment_repository.update.side_effect = (
        RuntimeError("Update error")
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="Update error",
    ):
        use_case.execute(dto)

    assert installment.stripe_invoice_id == "invoice-123"

    installment_repository.update.assert_called_once_with(
        installment
    )

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


def test_execute_rolls_back_when_commit_fails(
    use_case,
    financing_contract_repository,
    installment_repository,
    unit_of_work,
):
    contract = make_contract()

    installment = make_installment()

    installment_repository.find_by_stripe_invoice_id.return_value = None
    financing_contract_repository.get_by_subscription_id.return_value = (
        contract
    )
    installment_repository.find_next_unpaid.return_value = installment

    unit_of_work.commit.side_effect = (
        RuntimeError("Commit error")
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="Commit error",
    ):
        use_case.execute(dto)

    assert installment.stripe_invoice_id == "invoice-123"

    installment_repository.update.assert_called_once_with(
        installment
    )

    unit_of_work.commit.assert_called_once_with()
    unit_of_work.rollback.assert_called_once_with()