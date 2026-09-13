import pytest
from unittest.mock import Mock

from modules.applications.domain.enums import (
    ApplicationStatus,
    EventType,
)
from modules.applications.domain.exceptions import (
    ApplicationNotFound,
)
from modules.vehicles.domain.enums import VehicleStatus
from modules.leads.domain.enums import LeadStatus
from modules.payments.domain.exceptions import PaymentNotFound

from modules.payments.application.dtos.complete_sale_payment_dto import (
    CompleteSalePaymentDTO,
)
from modules.payments.application.results.complete_sale_payment_result import (
    CompleteSalePaymentResult,
)
from modules.warranties.application.dtos.activate_vehicle_warranty_dto import (
    ActivateVehicleWarrantyDTO,
)
from modules.financing.application.dtos.create_financing_contract_dto import (
    CreateFinancingContractDTO,
)
from modules.payments.application.dtos.create_subscription_dto import (
    CreateSubscriptionDTO,
)
from modules.financing.application.dtos.create_installments_dto import (
    CreateInstallmentsDTO,
)

from modules.payments.application.use_cases.complete_sale_payment import (
    CompleteSalePaymentUseCase,
)


@pytest.fixture
def vehicle_repository():
    return Mock()


@pytest.fixture
def application_repository():
    return Mock()


@pytest.fixture
def payment_repository():
    return Mock()


@pytest.fixture
def lead_repository():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def activate_vehicle_warranty_uc():
    return Mock()


@pytest.fixture
def create_financing_contract_uc():
    return Mock()


@pytest.fixture
def create_subscription_uc():
    return Mock()


@pytest.fixture
def create_installments_uc():
    return Mock()


@pytest.fixture
def use_case(
    vehicle_repository,
    application_repository,
    payment_repository,
    lead_repository,
    event_service,
    activate_vehicle_warranty_uc,
    create_financing_contract_uc,
    create_subscription_uc,
    create_installments_uc,
):
    return CompleteSalePaymentUseCase(
        vehicle_repository=vehicle_repository,
        application_repository=application_repository,
        payment_repository=payment_repository,
        lead_repository=lead_repository,
        event_service=event_service,
        activate_vehicle_warranty_uc=activate_vehicle_warranty_uc,
        create_financing_contract_uc=create_financing_contract_uc,
        create_subscription_uc=create_subscription_uc,
        create_installments_uc=create_installments_uc,
    )


def make_dto(
    application_id="application-123",
    payment_id="payment-123",
):
    return CompleteSalePaymentDTO(
        application_id=application_id,
        payment_id=payment_id,
    )


def make_vehicle(
    vehicle_id="vehicle-123",
):
    vehicle = Mock()
    vehicle.id = vehicle_id
    vehicle.mileage = 50000
    vehicle.status = VehicleStatus.AVAILABLE
    vehicle.is_available = True
    return vehicle


def make_payment(
    payment_id="payment-123",
    stripe_customer_id="cus-123",
):
    payment = Mock()
    payment.id = payment_id
    payment.stripe_customer_id = stripe_customer_id
    return payment


def make_application(
    application_id="application-123",
    user_id="user-123",
    vehicle=None,
    financing=None,
    quote_id=None,
    status=ApplicationStatus.APPROVED,
):
    application = Mock()

    application.id = application_id
    application.user_id = user_id
    application.vehicle = vehicle or make_vehicle()
    application.financing = financing
    application.quote_id = quote_id
    application.status = status

    return application


def make_financing(
    financed_amount=10000,
):
    financing = Mock()
    financing.financed_amount = financed_amount
    return financing


def make_contract_result(
    contract_id="contract-123",
):
    result = Mock()
    result.contract_id = contract_id
    return result


def test_complete_sale_payment_success_without_financing(
    use_case,
    vehicle_repository,
    application_repository,
    payment_repository,
    lead_repository,
    event_service,
    activate_vehicle_warranty_uc,
    create_financing_contract_uc,
    create_subscription_uc,
    create_installments_uc,
):
    vehicle = make_vehicle()
    application = make_application(
        vehicle=vehicle,
        financing=None,
        quote_id=None,
    )
    payment = make_payment()

    application_repository.get_by_id.return_value = application
    payment_repository.get_by_id.return_value = payment

    dto = make_dto()

    result = use_case.execute(dto)

    # Véhicule
    assert vehicle.status == VehicleStatus.SOLD
    assert vehicle.is_available is False

    vehicle_repository.update.assert_called_once_with(vehicle)

    # Application
    assert application.status == ApplicationStatus.COMPLETED

    application_repository.update.assert_called_once_with(
        application
    )

    # Paiement
    payment_repository.get_by_id.assert_called_once_with(
        "payment-123"
    )

    # Événement paiement
    event_service.log.assert_called_once_with(
        type=EventType.DEPOSIT_PAID,
        application_id="application-123",
        vehicle_id="vehicle-123",
        user_id="user-123",
        message="Acompte véhicule payé.",
        event_metadata={
            "payment_id": "payment-123",
            "vehicle_id": "vehicle-123",
        },
    )

    # Garantie
    activate_vehicle_warranty_uc.execute.assert_called_once_with(
        ActivateVehicleWarrantyDTO(
            vehicle_id="vehicle-123",
            mileage=50000,
            user_id="user-123",
        )
    )

    # Aucun financement
    create_financing_contract_uc.execute.assert_not_called()
    create_subscription_uc.execute.assert_not_called()
    create_installments_uc.execute.assert_not_called()

    # Résultat
    assert isinstance(
        result,
        CompleteSalePaymentResult,
    )
    assert result.application_id == "application-123"
    assert result.vehicle_id == "vehicle-123"
    assert result.warranty_created is True
    assert result.financing_created is False
    assert result.message == "Vente finalisée avec succès"


def test_complete_sale_payment_success_with_financing(
    use_case,
    vehicle_repository,
    application_repository,
    payment_repository,
    event_service,
    activate_vehicle_warranty_uc,
    create_financing_contract_uc,
    create_subscription_uc,
    create_installments_uc,
):
    vehicle = make_vehicle()

    financing = make_financing(
        financed_amount=10000
    )

    application = make_application(
        vehicle=vehicle,
        financing=financing,
    )

    payment = make_payment(
        stripe_customer_id="cus-456"
    )

    application_repository.get_by_id.return_value = application
    payment_repository.get_by_id.return_value = payment

    create_financing_contract_uc.execute.return_value = (
        make_contract_result("contract-456")
    )

    dto = make_dto()

    result = use_case.execute(dto)

    # Véhicule vendu
    assert vehicle.status == VehicleStatus.SOLD
    assert vehicle.is_available is False

    vehicle_repository.update.assert_called_once_with(
        vehicle
    )

    # Financement => application PAID
    assert application.status == ApplicationStatus.PAID

    application_repository.update.assert_called_once_with(
        application
    )

    # Contrat
    create_financing_contract_uc.execute.assert_called_once_with(
        CreateFinancingContractDTO(
            application_id="application-123",
        )
    )

    # Subscription
    create_subscription_uc.execute.assert_called_once_with(
        CreateSubscriptionDTO(
            contract_id="contract-456",
            stripe_customer_id="cus-456",
            user_id="user-123",
        )
    )

    # Échéances
    create_installments_uc.execute.assert_called_once_with(
        CreateInstallmentsDTO(
            contract_id="contract-456",
        )
    )

    # Résultat
    assert result.financing_created is True
    assert result.warranty_created is True
    assert result.message == "Vente finalisée avec succès"


def test_complete_sale_payment_raises_when_application_not_found(
    use_case,
    application_repository,
    payment_repository,
    vehicle_repository,
    event_service,
):
    application_repository.get_by_id.return_value = None

    dto = make_dto()

    with pytest.raises(ApplicationNotFound):
        use_case.execute(dto)

    application_repository.get_by_id.assert_called_once_with(
        "application-123"
    )

    payment_repository.get_by_id.assert_not_called()
    vehicle_repository.update.assert_not_called()
    event_service.log.assert_not_called()


def test_complete_sale_payment_raises_when_payment_not_found(
    use_case,
    application_repository,
    payment_repository,
    vehicle_repository,
    event_service,
):
    application = make_application()

    application_repository.get_by_id.return_value = application
    payment_repository.get_by_id.return_value = None

    dto = make_dto()

    with pytest.raises(PaymentNotFound):
        use_case.execute(dto)

    application_repository.get_by_id.assert_called_once_with(
        "application-123"
    )

    payment_repository.get_by_id.assert_called_once_with(
        "payment-123"
    )

    vehicle_repository.update.assert_not_called()
    application_repository.update.assert_not_called()
    event_service.log.assert_not_called()


def test_complete_sale_payment_is_idempotent_when_already_completed(
    use_case,
    application_repository,
    payment_repository,
    vehicle_repository,
    event_service,
    activate_vehicle_warranty_uc,
    create_financing_contract_uc,
    create_subscription_uc,
    create_installments_uc,
):
    vehicle = make_vehicle()

    application = make_application(
        vehicle=vehicle,
        financing=make_financing(),
        status=ApplicationStatus.COMPLETED,
    )

    payment = make_payment()

    application_repository.get_by_id.return_value = application
    payment_repository.get_by_id.return_value = payment

    dto = make_dto()

    result = use_case.execute(dto)

    assert isinstance(
        result,
        CompleteSalePaymentResult,
    )

    assert result.application_id == "application-123"
    assert result.vehicle_id == "vehicle-123"
    assert result.warranty_created is True
    assert result.financing_created is True
    assert result.message == "Vente déjà finalisée"

    vehicle_repository.update.assert_not_called()
    application_repository.update.assert_not_called()
    event_service.log.assert_not_called()

    activate_vehicle_warranty_uc.execute.assert_not_called()
    create_financing_contract_uc.execute.assert_not_called()
    create_subscription_uc.execute.assert_not_called()
    create_installments_uc.execute.assert_not_called()


def test_complete_sale_payment_marks_lead_as_won(
    use_case,
    application_repository,
    payment_repository,
    lead_repository,
    event_service,
    activate_vehicle_warranty_uc,
):
    vehicle = make_vehicle()

    application = make_application(
        vehicle=vehicle,
        quote_id="quote-123",
    )

    payment = make_payment()

    lead = Mock()
    lead.id = "lead-123"
    lead.assigned_to = "agent-123"
    lead.status = LeadStatus.CONTACTED

    application_repository.get_by_id.return_value = application
    payment_repository.get_by_id.return_value = payment
    lead_repository.get_by_quote_id.return_value = lead

    result = use_case.execute(
        make_dto()
    )

    assert lead.status == LeadStatus.WON

    lead_repository.get_by_quote_id.assert_called_once_with(
        "quote-123"
    )

    lead_repository.update.assert_called_once_with(
        lead
    )

    assert event_service.log.call_count == 2

    event_service.log.assert_any_call(
        type=EventType.LEAD_WON,
        application_id="application-123",
        vehicle_id="vehicle-123",
        quote_id="quote-123",
        lead_id="lead-123",
        user_id="agent-123",
        message="Lead converti après paiement",
        event_metadata={
            "lead_id": "lead-123",
            "quote_id": "quote-123",
        },
    )

    assert result.financing_created is False


def test_complete_sale_payment_does_not_update_lead_when_no_quote(
    use_case,
    application_repository,
    payment_repository,
    lead_repository,
):
    application = make_application(
        quote_id=None,
    )

    payment = make_payment()

    application_repository.get_by_id.return_value = application
    payment_repository.get_by_id.return_value = payment

    use_case.execute(
        make_dto()
    )

    lead_repository.get_by_quote_id.assert_not_called()
    lead_repository.update.assert_not_called()


def test_complete_sale_payment_propagates_warranty_error(
    use_case,
    application_repository,
    payment_repository,
    vehicle_repository,
    activate_vehicle_warranty_uc,
    create_financing_contract_uc,
    event_service,
):
    application = make_application()
    payment = make_payment()

    application_repository.get_by_id.return_value = application
    payment_repository.get_by_id.return_value = payment

    activate_vehicle_warranty_uc.execute.side_effect = (
        RuntimeError("Warranty error")
    )

    with pytest.raises(
        RuntimeError,
        match="Warranty error",
    ):
        use_case.execute(make_dto())

    vehicle_repository.update.assert_called_once_with(
        application.vehicle
    )

    application_repository.update.assert_called_once_with(
        application
    )

    event_service.log.assert_called_once()

    create_financing_contract_uc.execute.assert_not_called()


def test_complete_sale_payment_propagates_financing_contract_error(
    use_case,
    application_repository,
    payment_repository,
    create_financing_contract_uc,
    create_subscription_uc,
    create_installments_uc,
):
    application = make_application(
        financing=make_financing(10000),
    )

    payment = make_payment()

    application_repository.get_by_id.return_value = application
    payment_repository.get_by_id.return_value = payment

    create_financing_contract_uc.execute.side_effect = (
        RuntimeError("Financing contract error")
    )

    with pytest.raises(
        RuntimeError,
        match="Financing contract error",
    ):
        use_case.execute(make_dto())

    create_financing_contract_uc.execute.assert_called_once()

    create_subscription_uc.execute.assert_not_called()
    create_installments_uc.execute.assert_not_called()


def test_complete_sale_payment_propagates_subscription_error(
    use_case,
    application_repository,
    payment_repository,
    create_financing_contract_uc,
    create_subscription_uc,
    create_installments_uc,
):
    application = make_application(
        financing=make_financing(10000),
    )

    payment = make_payment()

    application_repository.get_by_id.return_value = application
    payment_repository.get_by_id.return_value = payment

    create_financing_contract_uc.execute.return_value = (
        make_contract_result("contract-123")
    )

    create_subscription_uc.execute.side_effect = (
        RuntimeError("Subscription error")
    )

    with pytest.raises(
        RuntimeError,
        match="Subscription error",
    ):
        use_case.execute(make_dto())

    create_financing_contract_uc.execute.assert_called_once()

    create_subscription_uc.execute.assert_called_once_with(
        CreateSubscriptionDTO(
            contract_id="contract-123",
            stripe_customer_id="cus-123",
            user_id="user-123",
        )
    )

    create_installments_uc.execute.assert_not_called()