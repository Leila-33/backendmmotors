import pytest
from unittest.mock import Mock, patch

from modules.applications.domain.enums import EventType
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.financing.domain.exceptions import FinancingContractNotFound
from modules.payments.application.dtos.create_subscription_dto import (
    CreateSubscriptionDTO,
)
from modules.payments.application.results.create_subscription_result import (
    CreateSubscriptionResult,
)
from modules.payments.domain.enums import PaymentStatus

from modules.payments.application.use_cases.create_subscription import (
    CreateSubscriptionUseCase,
)


@pytest.fixture
def stripe_service():
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
def use_case(
    stripe_service,
    financing_contract_repository,
    application_repository,
    event_service,
):
    return CreateSubscriptionUseCase(
        stripe_service=stripe_service,
        financing_contract_repository=financing_contract_repository,
        application_repository=application_repository,
        event_service=event_service,
    )


def make_dto(
    contract_id="contract-123",
    stripe_customer_id="cus-123",
    user_id="user-123",
):
    return CreateSubscriptionDTO(
        contract_id=contract_id,
        stripe_customer_id=stripe_customer_id,
        user_id=user_id,
    )


def make_contract(
    contract_id="contract-123",
    application_id="application-123",
    monthly_payment=350.00,
    stripe_customer_id=None,
    stripe_subscription_id=None,
    subscription_status=None,
):
    contract = Mock()

    contract.id = contract_id
    contract.application_id = application_id
    contract.monthly_payment = monthly_payment
    contract.stripe_customer_id = stripe_customer_id
    contract.stripe_subscription_id = stripe_subscription_id
    contract.subscription_status = subscription_status

    return contract


def make_application(
    application_id="application-123",
    vehicle_id="vehicle-123",
):
    application = Mock()

    application.id = application_id
    application.vehicle_id = vehicle_id

    return application


def make_subscription(
    subscription_id="sub-123",
    status="active",
):
    subscription = Mock()

    subscription.id = subscription_id
    subscription.status = status

    return subscription


def test_create_subscription_success(
    use_case,
    stripe_service,
    financing_contract_repository,
    application_repository,
    event_service,
):
    contract = make_contract(
        monthly_payment=350.00,
    )

    application = make_application()

    subscription = make_subscription(
        subscription_id="sub-123",
        status="active",
    )

    financing_contract_repository.find_by_id.return_value = contract
    application_repository.get_by_id.return_value = application
    stripe_service.create_subscription.return_value = subscription

    dto = make_dto(
        stripe_customer_id="cus-456",
    )

    with patch(
        "modules.payments.application.use_cases.create_subscription.SubscriptionStatusMapper.from_stripe",
        return_value=Mock(value="ACTIVE"),
    ) as mapper:

        result = use_case.execute(dto)

    # Contrat
    financing_contract_repository.find_by_id.assert_called_once_with(
        "contract-123"
    )

    # Application
    application_repository.get_by_id.assert_called_once_with(
        "application-123"
    )

    # Stripe
    stripe_service.create_subscription.assert_called_once_with(
        customer_id="cus-456",
        monthly_amount=350.00,
        application_id="application-123",
    )

    mapper.assert_called_once_with("active")

    # Contrat mis à jour
    assert contract.stripe_customer_id == "cus-456"
    assert contract.stripe_subscription_id == "sub-123"

    financing_contract_repository.update.assert_called_once_with(
        contract
    )

    # Événement
    event_service.log.assert_called_once_with(
        type=EventType.SUBSCRIPTION_CREATED,
        message="Abonnement de financement créé.",
        application_id="application-123",
        vehicle_id="vehicle-123",
        user_id="user-123",
        event_metadata={
            "contract_id": "contract-123",
            "stripe_customer_id": "cus-456",
            "stripe_subscription_id": "sub-123",
            "monthly_payment": 350.00,
        },
    )

    # Résultat
    assert isinstance(
        result,
        CreateSubscriptionResult,
    )

    assert result.contract_id == "contract-123"
    assert result.stripe_customer_id == "cus-456"
    assert result.stripe_subscription_id == "sub-123"
    assert result.subscription_status == "ACTIVE"


def test_create_subscription_raises_when_contract_not_found(
    use_case,
    financing_contract_repository,
    application_repository,
    stripe_service,
    event_service,
):
    financing_contract_repository.find_by_id.return_value = None

    dto = make_dto()

    with pytest.raises(FinancingContractNotFound):
        use_case.execute(dto)

    financing_contract_repository.find_by_id.assert_called_once_with(
        "contract-123"
    )

    application_repository.get_by_id.assert_not_called()
    stripe_service.create_subscription.assert_not_called()
    financing_contract_repository.update.assert_not_called()
    event_service.log.assert_not_called()


def test_create_subscription_is_idempotent(
    use_case,
    financing_contract_repository,
    application_repository,
    stripe_service,
    event_service,
):
    contract = make_contract(
        stripe_customer_id="cus-existing",
        stripe_subscription_id="sub-existing",
        subscription_status=Mock(value="ACTIVE"),
    )

    financing_contract_repository.find_by_id.return_value = contract

    dto = make_dto(
        stripe_customer_id="cus-new",
    )

    result = use_case.execute(dto)

    # Aucun accès à l'application nécessaire
    application_repository.get_by_id.assert_not_called()

    # Aucun nouvel abonnement Stripe
    stripe_service.create_subscription.assert_not_called()

    # Aucun update
    financing_contract_repository.update.assert_not_called()

    # Aucun événement
    event_service.log.assert_not_called()

    assert isinstance(
        result,
        CreateSubscriptionResult,
    )

    assert result.contract_id == "contract-123"
    assert result.stripe_customer_id == "cus-existing"
    assert result.stripe_subscription_id == "sub-existing"
    assert result.subscription_status == "ACTIVE"


def test_create_subscription_returns_none_status_when_existing_contract_status_is_none(
    use_case,
    financing_contract_repository,
):
    contract = make_contract(
        stripe_customer_id="cus-existing",
        stripe_subscription_id="sub-existing",
        subscription_status=None,
    )

    financing_contract_repository.find_by_id.return_value = contract

    result = use_case.execute(
        make_dto()
    )

    assert result.contract_id == "contract-123"
    assert result.stripe_customer_id == "cus-existing"
    assert result.stripe_subscription_id == "sub-existing"
    assert result.subscription_status is None


def test_create_subscription_raises_when_application_not_found(
    use_case,
    financing_contract_repository,
    application_repository,
    stripe_service,
    event_service,
):
    contract = make_contract()

    financing_contract_repository.find_by_id.return_value = contract
    application_repository.get_by_id.return_value = None

    dto = make_dto()

    with pytest.raises(ApplicationNotFound):
        use_case.execute(dto)

    application_repository.get_by_id.assert_called_once_with(
        "application-123"
    )

    stripe_service.create_subscription.assert_not_called()
    financing_contract_repository.update.assert_not_called()
    event_service.log.assert_not_called()


def test_create_subscription_propagates_stripe_error(
    use_case,
    financing_contract_repository,
    application_repository,
    stripe_service,
    event_service,
):
    contract = make_contract()
    application = make_application()

    financing_contract_repository.find_by_id.return_value = contract
    application_repository.get_by_id.return_value = application

    stripe_service.create_subscription.side_effect = (
        RuntimeError("Stripe error")
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="Stripe error",
    ):
        use_case.execute(dto)

    stripe_service.create_subscription.assert_called_once_with(
        customer_id="cus-123",
        monthly_amount=350.00,
        application_id="application-123",
    )

    financing_contract_repository.update.assert_not_called()
    event_service.log.assert_not_called()


def test_create_subscription_propagates_contract_update_error(
    use_case,
    financing_contract_repository,
    application_repository,
    stripe_service,
    event_service,
):
    contract = make_contract()
    application = make_application()
    subscription = make_subscription()

    financing_contract_repository.find_by_id.return_value = contract
    application_repository.get_by_id.return_value = application
    stripe_service.create_subscription.return_value = subscription

    financing_contract_repository.update.side_effect = (
        RuntimeError("Update error")
    )

    dto = make_dto()

    with patch(
        "modules.payments.application.use_cases.create_subscription.SubscriptionStatusMapper.from_stripe",
        return_value=Mock(value="ACTIVE"),
    ):

        with pytest.raises(
            RuntimeError,
            match="Update error",
        ):
            use_case.execute(dto)

    financing_contract_repository.update.assert_called_once_with(
        contract
    )

    event_service.log.assert_not_called()


def test_create_subscription_propagates_event_error(
    use_case,
    financing_contract_repository,
    application_repository,
    stripe_service,
    event_service,
):
    contract = make_contract()
    application = make_application()
    subscription = make_subscription(
        subscription_id="sub-123",
        status="active",
    )

    financing_contract_repository.find_by_id.return_value = contract
    application_repository.get_by_id.return_value = application
    stripe_service.create_subscription.return_value = subscription

    event_service.log.side_effect = RuntimeError(
        "Event error"
    )

    dto = make_dto()

    with patch(
        "modules.payments.application.use_cases.create_subscription.SubscriptionStatusMapper.from_stripe",
        return_value=Mock(value="ACTIVE"),
    ):

        with pytest.raises(
            RuntimeError,
            match="Event error",
        ):
            use_case.execute(dto)

    financing_contract_repository.update.assert_called_once_with(
        contract
    )

    event_service.log.assert_called_once()

    # L'événement échoue après la mise à jour du contrat.
    assert contract.stripe_customer_id == "cus-123"
    assert contract.stripe_subscription_id == "sub-123"