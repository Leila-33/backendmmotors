from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from modules.applications.domain.enums import (
    ApplicationStatus,
    EventType,
)
from modules.financing.domain.enums import InstallmentStatus
from modules.financing.domain.exceptions import (
    FinancingContractNotFound,
    InstallmentNotFound,
)
from modules.payments.domain.enums import SubscriptionStatus
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.payments.application.use_cases.handle_subscription_payment import (
    HandleSubscriptionPaymentUseCase,
)


def make_dto(
    invoice_id="invoice-123",
    subscription_id="sub-123",
    event_type="invoice.paid",
):
    dto = Mock()
    dto.invoice_id = invoice_id
    dto.subscription_id = subscription_id
    dto.event_type = event_type
    return dto


def make_installment(
    installment_id="installment-123",
    contract_id="contract-123",
    status=InstallmentStatus.PENDING,
    amount=100,
    number=1,
    stripe_invoice_id="invoice-123",
):
    installment = Mock()

    installment.id = installment_id
    installment.financing_contract_id = contract_id
    installment.status = status
    installment.amount = amount
    installment.installment_number = number
    installment.stripe_invoice_id = stripe_invoice_id
    installment.paid_at = None

    return installment


def make_contract(
    contract_id="contract-123",
    application_id="application-123",
    remaining_balance=500,
    subscription_status=SubscriptionStatus.ACTIVE,
):
    contract = Mock()

    contract.id = contract_id
    contract.application_id = application_id
    contract.remaining_balance = remaining_balance
    contract.subscription_status = subscription_status

    return contract


def make_application(
    application_id="application-123",
    user_id="user-123",
    vehicle_id="vehicle-123",
):
    application = Mock()

    application.id = application_id
    application.user_id = user_id
    application.vehicle_id = vehicle_id
    application.status = ApplicationStatus.APPROVED

    return application


@pytest.fixture
def installment_repository():
    return Mock()


@pytest.fixture
def financing_contract_repository():
    return Mock()


@pytest.fixture
def application_repository():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    installment_repository,
    financing_contract_repository,
    application_repository,
    event_service,
    unit_of_work,
):
    return HandleSubscriptionPaymentUseCase(
        installment_repository=installment_repository,
        financing_contract_repository=financing_contract_repository,
        application_repository=application_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


# ============================================================
# SUCCESS - invoice.paid
# ============================================================


def test_execute_invoice_paid_success(
    use_case,
    installment_repository,
    financing_contract_repository,
    application_repository,
    event_service,
    unit_of_work,
):
    installment = make_installment(
        status=InstallmentStatus.PENDING,
        amount=100,
        number=3,
    )
    contract = make_contract(
        remaining_balance=500,
    )
    application = make_application()

    installment_repository.find_by_stripe_invoice_id.return_value = (
        installment
    )
    financing_contract_repository.find_by_id.return_value = contract
    application_repository.get_by_id.return_value = application

    dto = make_dto()

    result = use_case.execute(dto)

    assert result.installment_id == installment.id
    assert result.status == InstallmentStatus.PAID.value
    assert result.invoice_id == dto.invoice_id
    assert result.message == "Mensualité payée"

    assert installment.status == InstallmentStatus.PAID
    assert isinstance(installment.paid_at, datetime)
    assert installment.paid_at.tzinfo == timezone.utc

    assert contract.remaining_balance == 400

    installment_repository.update.assert_called_once_with(
        installment
    )

    financing_contract_repository.update.assert_called_once_with(
        contract
    )

    event_service.log.assert_called_once_with(
        application_id=application.id,
        user_id=application.user_id,
        vehicle_id=application.vehicle_id,
        type=EventType.INSTALLMENT_PAID,
        message="Mensualité n°3 payée.",
        event_metadata={
            "contract_id": contract.id,
            "installment_id": installment.id,
            "invoice_id": dto.invoice_id,
        },
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# SUCCESS - financement terminé
# ============================================================


def test_execute_completes_financing_when_balance_reaches_zero(
    use_case,
    installment_repository,
    financing_contract_repository,
    application_repository,
    event_service,
    unit_of_work,
):
    installment = make_installment(
        status=InstallmentStatus.PENDING,
        amount=500,
        number=5,
    )

    contract = make_contract(
        remaining_balance=500,
    )

    application = make_application()

    installment_repository.find_by_stripe_invoice_id.return_value = (
        installment
    )
    financing_contract_repository.find_by_id.return_value = contract
    application_repository.get_by_id.return_value = application

    dto = make_dto()

    result = use_case.execute(dto)

    assert result.status == InstallmentStatus.PAID.value
    assert result.message == "Mensualité payée"

    assert contract.remaining_balance == 0
    assert contract.subscription_status == (
        SubscriptionStatus.COMPLETED
    )

    assert application.status == ApplicationStatus.COMPLETED

    # Une mise à jour après le paiement
    # + une mise à jour lors de la finalisation.
    assert (
        financing_contract_repository.update.call_count
        == 2
    )

    application_repository.update.assert_called_once_with(
        application
    )

    assert event_service.log.call_count == 2

    calls = event_service.log.call_args_list

    assert calls[0].kwargs["type"] == (
        EventType.INSTALLMENT_PAID
    )

    assert calls[1].kwargs["type"] == (
        EventType.FINANCING_COMPLETED
    )

    assert calls[1].kwargs["message"] == (
        "Financement intégralement remboursé."
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# BALANCE NE DESCEND PAS SOUS ZERO
# ============================================================


def test_execute_clamps_remaining_balance_to_zero(
    use_case,
    installment_repository,
    financing_contract_repository,
    application_repository,
):
    installment = make_installment(
        status=InstallmentStatus.PENDING,
        amount=700,
    )

    contract = make_contract(
        remaining_balance=500,
    )

    application = make_application()

    installment_repository.find_by_stripe_invoice_id.return_value = (
        installment
    )
    financing_contract_repository.find_by_id.return_value = contract
    application_repository.get_by_id.return_value = application

    result = use_case.execute(make_dto())

    assert result.status == InstallmentStatus.PAID.value
    assert contract.remaining_balance == 0


# ============================================================
# IDEMPOTENCE - invoice.paid déjà payé
# ============================================================


def test_execute_invoice_paid_already_paid(
    use_case,
    installment_repository,
    financing_contract_repository,
    application_repository,
    event_service,
    unit_of_work,
):
    installment = make_installment(
        status=InstallmentStatus.PAID,
    )

    contract = make_contract()
    application = make_application()

    installment_repository.find_by_stripe_invoice_id.return_value = (
        installment
    )
    financing_contract_repository.find_by_id.return_value = contract
    application_repository.get_by_id.return_value = application

    result = use_case.execute(make_dto())

    assert result.installment_id == installment.id
    assert result.status == InstallmentStatus.PAID.value
    assert result.message == "Mensualité déjà payée"

    installment_repository.update.assert_not_called()
    financing_contract_repository.update.assert_not_called()
    application_repository.update.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# PAYMENT FAILED
# ============================================================


def test_execute_invoice_payment_failed(
    use_case,
    installment_repository,
    financing_contract_repository,
    application_repository,
    event_service,
    unit_of_work,
):
    installment = make_installment(
        status=InstallmentStatus.PENDING,
        number=4,
    )

    contract = make_contract()
    application = make_application()

    installment_repository.find_by_stripe_invoice_id.return_value = (
        installment
    )
    financing_contract_repository.find_by_id.return_value = contract
    application_repository.get_by_id.return_value = application

    dto = make_dto(
        event_type="invoice.payment_failed"
    )

    result = use_case.execute(dto)

    assert result.installment_id == installment.id
    assert result.status == InstallmentStatus.FAILED.value
    assert result.invoice_id == dto.invoice_id
    assert result.message == (
        "Paiement de la mensualité échoué"
    )

    assert installment.status == InstallmentStatus.FAILED

    installment_repository.update.assert_called_once_with(
        installment
    )

    financing_contract_repository.update.assert_not_called()
    application_repository.update.assert_not_called()

    event_service.log.assert_called_once_with(
        application_id=application.id,
        user_id=application.user_id,
        vehicle_id=application.vehicle_id,
        type=EventType.INSTALLMENT_FAILED,
        message=(
            "Le paiement de la mensualité "
            "n°4 a échoué."
        ),
        event_metadata={
            "contract_id": contract.id,
            "installment_id": installment.id,
            "invoice_id": dto.invoice_id,
        },
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# PAYMENT FAILED - mensualité déjà payée
# ============================================================


def test_execute_payment_failed_for_already_paid_installment(
    use_case,
    installment_repository,
    financing_contract_repository,
    application_repository,
    event_service,
    unit_of_work,
):
    installment = make_installment(
        status=InstallmentStatus.PAID,
    )

    contract = make_contract()
    application = make_application()

    installment_repository.find_by_stripe_invoice_id.return_value = (
        installment
    )
    financing_contract_repository.find_by_id.return_value = contract
    application_repository.get_by_id.return_value = application

    dto = make_dto(
        event_type="invoice.payment_failed"
    )

    result = use_case.execute(dto)

    assert result.status == InstallmentStatus.PAID.value
    assert result.message == "Mensualité déjà payée"

    installment_repository.update.assert_not_called()
    financing_contract_repository.update.assert_not_called()
    application_repository.update.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# FALLBACK - facture non associée
# ============================================================


def test_execute_fallback_finds_next_unpaid_installment(
    use_case,
    installment_repository,
    financing_contract_repository,
    application_repository,
    event_service,
    unit_of_work,
):
    installment = make_installment(
        stripe_invoice_id=None,
        status=InstallmentStatus.PENDING,
        number=2,
    )

    contract = make_contract(
        remaining_balance=300,
    )

    application = make_application()

    # La facture n'est pas encore associée.
    installment_repository.find_by_stripe_invoice_id.return_value = (
        None
    )

    financing_contract_repository.get_by_subscription_id.return_value = (
        contract
    )

    installment_repository.find_next_unpaid.return_value = (
        installment
    )

    application_repository.get_by_id.return_value = application

    # Important :
    # après le fallback, le code utilise contract directement
    # et ne fait donc pas find_by_id().
    dto = make_dto()

    result = use_case.execute(dto)

    assert result.installment_id == installment.id
    assert result.status == InstallmentStatus.PAID.value

    assert installment.stripe_invoice_id == dto.invoice_id
    assert installment.status == InstallmentStatus.PAID

    assert (
        installment_repository.find_by_stripe_invoice_id
        .assert_called_once_with(dto.invoice_id)
        is None
    )

    financing_contract_repository.get_by_subscription_id.assert_called_once_with(
        dto.subscription_id
    )

    installment_repository.find_next_unpaid.assert_called_once_with(
        contract.id
    )

    # update une première fois pour associer la facture,
    # puis une deuxième fois pour passer la mensualité à PAID.
    assert installment_repository.update.call_count == 2

    assert contract.remaining_balance == 200

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# FALLBACK - subscription_id absent
# ============================================================


def test_execute_fallback_without_subscription_id_raises(
    use_case,
    installment_repository,
    financing_contract_repository,
    unit_of_work,
):
    installment_repository.find_by_stripe_invoice_id.return_value = (
        None
    )

    dto = make_dto(
        subscription_id=None,
    )

    with pytest.raises(InstallmentNotFound):
        use_case.execute(dto)

    financing_contract_repository.get_by_subscription_id.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# FALLBACK - contrat introuvable
# ============================================================


def test_execute_fallback_contract_not_found(
    use_case,
    installment_repository,
    financing_contract_repository,
    unit_of_work,
):
    installment_repository.find_by_stripe_invoice_id.return_value = (
        None
    )

    financing_contract_repository.get_by_subscription_id.return_value = (
        None
    )

    dto = make_dto()

    with pytest.raises(FinancingContractNotFound):
        use_case.execute(dto)

    installment_repository.find_next_unpaid.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# FALLBACK - aucune mensualité impayée
# ============================================================


def test_execute_fallback_no_unpaid_installment(
    use_case,
    installment_repository,
    financing_contract_repository,
    unit_of_work,
):
    contract = make_contract()

    installment_repository.find_by_stripe_invoice_id.return_value = (
        None
    )

    financing_contract_repository.get_by_subscription_id.return_value = (
        contract
    )

    installment_repository.find_next_unpaid.return_value = None

    dto = make_dto()

    with pytest.raises(InstallmentNotFound):
        use_case.execute(dto)

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# CONTRAT INTROUVABLE APRÈS RÉCUPÉRATION DE L'INSTALLMENT
# ============================================================


def test_execute_contract_not_found_from_installment(
    use_case,
    installment_repository,
    financing_contract_repository,
    application_repository,
    unit_of_work,
):
    installment = make_installment()

    installment_repository.find_by_stripe_invoice_id.return_value = (
        installment
    )

    financing_contract_repository.find_by_id.return_value = (
        None
    )

    with pytest.raises(FinancingContractNotFound):
        use_case.execute(make_dto())

    application_repository.get_by_id.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# APPLICATION INTROUVABLE
# ============================================================


def test_execute_application_not_found(
    use_case,
    installment_repository,
    financing_contract_repository,
    application_repository,
    unit_of_work,
):
    installment = make_installment()
    contract = make_contract()

    installment_repository.find_by_stripe_invoice_id.return_value = (
        installment
    )
    financing_contract_repository.find_by_id.return_value = (
        contract
    )
    application_repository.get_by_id.return_value = None

    with pytest.raises(ApplicationNotFound):
        use_case.execute(make_dto())

    installment_repository.update.assert_not_called()
    event_service = use_case.event_service
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# ÉVÉNEMENT INCONNU
# ============================================================


def test_execute_unknown_event_returns_none(
    use_case,
    installment_repository,
    financing_contract_repository,
    application_repository,
    event_service,
    unit_of_work,
):
    installment = make_installment(
        status=InstallmentStatus.PENDING
    )
    contract = make_contract()
    application = make_application()

    installment_repository.find_by_stripe_invoice_id.return_value = (
        installment
    )
    financing_contract_repository.find_by_id.return_value = (
        contract
    )
    application_repository.get_by_id.return_value = application

    dto = make_dto(
        event_type="invoice.unknown"
    )

    result = use_case.execute(dto)

    assert result is None

    installment_repository.update.assert_not_called()
    financing_contract_repository.update.assert_not_called()
    application_repository.update.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# ERREUR REPOSITORY INSTALLMENT
# ============================================================


def test_execute_installment_repository_error_rolls_back(
    use_case,
    installment_repository,
    unit_of_work,
):
    installment_repository.find_by_stripe_invoice_id.side_effect = (
        RuntimeError("DB error")
    )

    with pytest.raises(RuntimeError, match="DB error"):
        use_case.execute(make_dto())

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# ERREUR UPDATE INSTALLMENT
# ============================================================


def test_execute_installment_update_error_rolls_back(
    use_case,
    installment_repository,
    financing_contract_repository,
    application_repository,
    unit_of_work,
):
    installment = make_installment()
    contract = make_contract()
    application = make_application()

    installment_repository.find_by_stripe_invoice_id.return_value = (
        installment
    )
    financing_contract_repository.find_by_id.return_value = (
        contract
    )
    application_repository.get_by_id.return_value = application

    installment_repository.update.side_effect = RuntimeError(
        "Update error"
    )

    with pytest.raises(RuntimeError, match="Update error"):
        use_case.execute(make_dto())

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# ERREUR EVENT
# ============================================================


def test_execute_event_error_rolls_back(
    use_case,
    installment_repository,
    financing_contract_repository,
    application_repository,
    event_service,
    unit_of_work,
):
    installment = make_installment()
    contract = make_contract()
    application = make_application()

    installment_repository.find_by_stripe_invoice_id.return_value = (
        installment
    )
    financing_contract_repository.find_by_id.return_value = (
        contract
    )
    application_repository.get_by_id.return_value = application

    event_service.log.side_effect = RuntimeError(
        "Event error"
    )

    with pytest.raises(RuntimeError, match="Event error"):
        use_case.execute(make_dto())

    assert installment.status == InstallmentStatus.PAID
    assert contract.remaining_balance == 400

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# ERREUR COMMIT
# ============================================================


def test_execute_commit_error_rolls_back(
    use_case,
    installment_repository,
    financing_contract_repository,
    application_repository,
    unit_of_work,
):
    installment = make_installment()
    contract = make_contract()
    application = make_application()

    installment_repository.find_by_stripe_invoice_id.return_value = (
        installment
    )
    financing_contract_repository.find_by_id.return_value = (
        contract
    )
    application_repository.get_by_id.return_value = application

    unit_of_work.commit.side_effect = RuntimeError(
        "Commit error"
    )

    with pytest.raises(RuntimeError, match="Commit error"):
        use_case.execute(make_dto())

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()