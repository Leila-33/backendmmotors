from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from modules.applications.domain.enums import (
    ApplicationStatus,
    EventType,
)
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.financing.application.dtos.create_financing_contract_dto import (
    CreateFinancingContractDTO,
)
from modules.financing.application.dtos.create_installments_dto import (
    CreateInstallmentsDTO,
)
from modules.leads.domain.enums import LeadStatus
from modules.payments.application.dtos.complete_sale_payment_dto import (
    CompleteSalePaymentDTO,
)
from modules.payments.application.dtos.create_subscription_dto import (
    CreateSubscriptionDTO,
)
from modules.payments.application.dtos.complete_sale_payment_dto import (
    CompleteSalePaymentDTO,
)
from modules.payments.application.results.complete_sale_payment_result import (
    CompleteSalePaymentResult,
)
from modules.payments.application.use_cases.complete_sale_payment import (
    CompleteSalePaymentUseCase,
)
from modules.payments.domain.exceptions import PaymentNotFound
from modules.vehicles.domain.enums import VehicleStatus
from modules.warranties.application.dtos.activate_vehicle_warranty_dto import (
    ActivateVehicleWarrantyDTO,
)


class TestCompleteSalePaymentUseCase:

    def setup_method(self):
        self.vehicle_repository = MagicMock()
        self.application_repository = MagicMock()
        self.payment_repository = MagicMock()
        self.lead_repository = MagicMock()
        self.event_service = MagicMock()

        self.activate_vehicle_warranty_uc = MagicMock()
        self.create_financing_contract_uc = MagicMock()
        self.create_subscription_uc = MagicMock()
        self.create_installments_uc = MagicMock()

        self.use_case = CompleteSalePaymentUseCase(
            vehicle_repository=self.vehicle_repository,
            application_repository=self.application_repository,
            payment_repository=self.payment_repository,
            lead_repository=self.lead_repository,
            event_service=self.event_service,
            activate_vehicle_warranty_uc=(
                self.activate_vehicle_warranty_uc
            ),
            create_financing_contract_uc=(
                self.create_financing_contract_uc
            ),
            create_subscription_uc=(
                self.create_subscription_uc
            ),
            create_installments_uc=(
                self.create_installments_uc
            ),
        )

        self.dto = CompleteSalePaymentDTO(
            application_id="application-123",
            payment_id="payment-123",
        )

    # ==========================================================
    # HELPERS
    # ==========================================================

    def create_vehicle(self):
        vehicle = MagicMock()

        vehicle.id = "vehicle-123"
        vehicle.mileage = 85000
        vehicle.status = VehicleStatus.PUBLISHED
        vehicle.is_available = True

        return vehicle

    def create_application(
        self,
        financing=None,
        status=ApplicationStatus.APPROVED,
        quote_id=None,
    ):
        application = MagicMock()

        application.id = "application-123"
        application.user_id = "customer-123"
        application.status = status
        application.vehicle = self.create_vehicle()
        application.financing = financing
        application.quote_id = quote_id

        return application

    def create_payment(self):
        payment = MagicMock()

        payment.id = "payment-123"
        payment.stripe_customer_id = "cus-123"

        return payment

    # ==========================================================
    # VENTE COMPTANT
    # ==========================================================

    def test_completes_cash_sale_successfully(self):
        # Arrange
        application = self.create_application(
            financing=None
        )
        payment = self.create_payment()

        self.application_repository.get_by_id.return_value = application
        self.payment_repository.get_by_id.return_value = payment

        # Act
        result = self.use_case.execute(self.dto)

        # Assert
        assert isinstance(
            result,
            CompleteSalePaymentResult,
        )

        assert result.application_id == application.id
        assert result.vehicle_id == application.vehicle.id
        assert result.warranty_created is True
        assert result.financing_created is False
        assert result.assigned_agent_id is None
        assert result.message == "Vente finalisée avec succès"

        # Vehicle
        assert application.vehicle.status == VehicleStatus.SOLD
        assert application.vehicle.is_available is False

        self.vehicle_repository.update.assert_called_once_with(
            application.vehicle
        )

        # Application
        assert application.status == ApplicationStatus.COMPLETED

        self.application_repository.update.assert_called_once_with(
            application
        )

        # Warranty
        self.activate_vehicle_warranty_uc.execute.assert_called_once()

        warranty_dto = (
            self.activate_vehicle_warranty_uc
            .execute
            .call_args
            .args[0]
        )

        assert isinstance(
            warranty_dto,
            ActivateVehicleWarrantyDTO,
        )

        assert warranty_dto.vehicle_id == application.vehicle.id
        assert warranty_dto.mileage == application.vehicle.mileage
        assert warranty_dto.user_id == application.user_id

        # Financing
        self.create_financing_contract_uc.execute.assert_not_called()
        self.create_subscription_uc.execute.assert_not_called()
        self.create_installments_uc.execute.assert_not_called()

    # ==========================================================
    # VENTE FINANCÉE
    # ==========================================================

    def test_completes_financed_sale_successfully(self):
        # Arrange
        financing = MagicMock()
        financing.financed_amount = 15000

        application = self.create_application(
            financing=financing
        )
        payment = self.create_payment()

        contract_result = SimpleNamespace(
            contract_id="contract-123"
        )

        self.application_repository.get_by_id.return_value = application
        self.payment_repository.get_by_id.return_value = payment

        self.create_financing_contract_uc.execute.return_value = (
            contract_result
        )

        # Act
        result = self.use_case.execute(self.dto)

        # Assert
        assert result.application_id == application.id
        assert result.vehicle_id == application.vehicle.id
        assert result.warranty_created is True
        assert result.financing_created is True
        assert result.message == "Vente finalisée avec succès"

        # Application
        assert application.status == ApplicationStatus.PAID

        self.application_repository.update.assert_called_once_with(
            application
        )

        # Financing contract
        self.create_financing_contract_uc.execute.assert_called_once()

        contract_dto = (
            self.create_financing_contract_uc
            .execute
            .call_args
            .args[0]
        )

        assert isinstance(
            contract_dto,
            CreateFinancingContractDTO,
        )

        assert contract_dto.application_id == application.id

        # Subscription
        self.create_subscription_uc.execute.assert_called_once()

        subscription_dto = (
            self.create_subscription_uc
            .execute
            .call_args
            .args[0]
        )

        assert isinstance(
            subscription_dto,
            CreateSubscriptionDTO,
        )

        assert subscription_dto.contract_id == "contract-123"
        assert subscription_dto.stripe_customer_id == (
            payment.stripe_customer_id
        )
        assert subscription_dto.user_id == application.user_id

        # Installments
        self.create_installments_uc.execute.assert_called_once()

        installments_dto = (
            self.create_installments_uc
            .execute
            .call_args
            .args[0]
        )

        assert isinstance(
            installments_dto,
            CreateInstallmentsDTO,
        )

        assert installments_dto.contract_id == "contract-123"

    # ==========================================================
    # APPLICATION INTROUVABLE
    # ==========================================================

    def test_raises_application_not_found(self):
        # Arrange
        self.application_repository.get_by_id.return_value = None

        # Act / Assert
        with pytest.raises(ApplicationNotFound):
            self.use_case.execute(self.dto)

        self.application_repository.get_by_id.assert_called_once_with(
            self.dto.application_id
        )

        self.payment_repository.get_by_id.assert_not_called()

        self.vehicle_repository.update.assert_not_called()
        self.application_repository.update.assert_not_called()

        self.activate_vehicle_warranty_uc.execute.assert_not_called()

    # ==========================================================
    # PAYMENT INTROUVABLE
    # ==========================================================

    def test_raises_payment_not_found(self):
        # Arrange
        application = self.create_application()

        self.application_repository.get_by_id.return_value = application
        self.payment_repository.get_by_id.return_value = None

        # Act / Assert
        with pytest.raises(PaymentNotFound):
            self.use_case.execute(self.dto)

        self.payment_repository.get_by_id.assert_called_once_with(
            self.dto.payment_id
        )

        self.vehicle_repository.update.assert_not_called()
        self.application_repository.update.assert_not_called()

        self.activate_vehicle_warranty_uc.execute.assert_not_called()

    # ==========================================================
    # IDEMPOTENCE
    # ==========================================================

    def test_returns_already_completed_when_application_is_completed(self):
        # Arrange
        application = self.create_application(
            status=ApplicationStatus.COMPLETED,
            financing=None,
        )
        payment = self.create_payment()

        self.application_repository.get_by_id.return_value = application
        self.payment_repository.get_by_id.return_value = payment

        # Act
        result = self.use_case.execute(self.dto)

        # Assert
        assert result.application_id == application.id
        assert result.vehicle_id == application.vehicle.id
        assert result.warranty_created is True
        assert result.financing_created is False
        assert result.message == "Vente déjà finalisée"

        self.vehicle_repository.update.assert_not_called()
        self.application_repository.update.assert_not_called()

        self.event_service.log.assert_not_called()

        self.activate_vehicle_warranty_uc.execute.assert_not_called()

        self.create_financing_contract_uc.execute.assert_not_called()
        self.create_subscription_uc.execute.assert_not_called()
        self.create_installments_uc.execute.assert_not_called()

    # ==========================================================
    # VÉHICULE VENDU
    # ==========================================================

    def test_marks_vehicle_as_sold_and_unavailable(self):
        # Arrange
        application = self.create_application()
        payment = self.create_payment()

        self.application_repository.get_by_id.return_value = application
        self.payment_repository.get_by_id.return_value = payment

        # Act
        self.use_case.execute(self.dto)

        # Assert
        assert application.vehicle.status == VehicleStatus.SOLD
        assert application.vehicle.is_available is False

        self.vehicle_repository.update.assert_called_once_with(
            application.vehicle
        )

    # ==========================================================
    # APPLICATION COMPLETED - COMPTANT
    # ==========================================================

    def test_sets_application_to_completed_for_cash_sale(self):
        # Arrange
        application = self.create_application(
            financing=None
        )
        payment = self.create_payment()

        self.application_repository.get_by_id.return_value = application
        self.payment_repository.get_by_id.return_value = payment

        # Act
        self.use_case.execute(self.dto)

        # Assert
        assert application.status == ApplicationStatus.COMPLETED

    # ==========================================================
    # APPLICATION PAID - FINANCEMENT
    # ==========================================================

    def test_sets_application_to_paid_for_financed_sale(self):
        # Arrange
        financing = MagicMock()
        financing.financed_amount = 20000

        application = self.create_application(
            financing=financing
        )
        payment = self.create_payment()

        self.application_repository.get_by_id.return_value = application
        self.payment_repository.get_by_id.return_value = payment

        self.create_financing_contract_uc.execute.return_value = (
            SimpleNamespace(contract_id="contract-123")
        )

        # Act
        self.use_case.execute(self.dto)

        # Assert
        assert application.status == ApplicationStatus.PAID

    # ==========================================================
    # FINANCEMENT À 0
    # ==========================================================

    def test_treats_zero_financed_amount_as_cash_sale(self):
        # Arrange
        financing = MagicMock()
        financing.financed_amount = 0

        application = self.create_application(
            financing=financing
        )
        payment = self.create_payment()

        self.application_repository.get_by_id.return_value = application
        self.payment_repository.get_by_id.return_value = payment

        # Act
        result = self.use_case.execute(self.dto)

        # Assert
        assert result.financing_created is False
        assert application.status == ApplicationStatus.COMPLETED

        self.create_financing_contract_uc.execute.assert_not_called()
        self.create_subscription_uc.execute.assert_not_called()
        self.create_installments_uc.execute.assert_not_called()

    # ==========================================================
    # EVENT DE PAIEMENT
    # ==========================================================

    def test_logs_deposit_paid_event(self):
        # Arrange
        application = self.create_application()
        payment = self.create_payment()

        self.application_repository.get_by_id.return_value = application
        self.payment_repository.get_by_id.return_value = payment

        # Act
        self.use_case.execute(self.dto)

        # Assert
        self.event_service.log.assert_any_call(
            type=EventType.DEPOSIT_PAID,
            application_id=application.id,
            vehicle_id=application.vehicle.id,
            user_id=application.user_id,
            message="Acompte véhicule payé.",
            event_metadata={
                "payment_id": self.dto.payment_id,
                "vehicle_id": application.vehicle.id,
            },
        )

    # ==========================================================
    # LEAD WON
    # ==========================================================

    def test_marks_lead_as_won_when_application_has_quote(self):
        # Arrange
        application = self.create_application(
            quote_id="quote-123"
        )
        payment = self.create_payment()

        lead = MagicMock()
        lead.id = "lead-123"
        lead.assigned_to = "agent-123"
        lead.status = LeadStatus.NEW

        self.application_repository.get_by_id.return_value = application
        self.payment_repository.get_by_id.return_value = payment

        self.lead_repository.get_by_quote_id.return_value = lead

        # Act
        result = self.use_case.execute(self.dto)

        # Assert
        assert result.assigned_agent_id == "agent-123"

        assert lead.status == LeadStatus.WON

        self.lead_repository.update.assert_called_once_with(
            lead
        )

        self.lead_repository.get_by_quote_id.assert_called_once_with(
            application.quote_id
        )

        self.event_service.log.assert_any_call(
            type=EventType.LEAD_WON,
            application_id=application.id,
            vehicle_id=application.vehicle.id,
            quote_id=application.quote_id,
            lead_id=lead.id,
            user_id=lead.assigned_to,
            message="Lead converti après paiement",
            event_metadata={
                "lead_id": lead.id,
                "quote_id": application.quote_id,
            },
        )

    # ==========================================================
    # QUOTE SANS LEAD
    # ==========================================================

    def test_does_not_update_lead_when_quote_has_no_lead(self):
        # Arrange
        application = self.create_application(
            quote_id="quote-123"
        )
        payment = self.create_payment()

        self.application_repository.get_by_id.return_value = application
        self.payment_repository.get_by_id.return_value = payment

        self.lead_repository.get_by_quote_id.return_value = None

        # Act
        result = self.use_case.execute(self.dto)

        # Assert
        assert result.assigned_agent_id is None

        self.lead_repository.get_by_quote_id.assert_called_once_with(
            application.quote_id
        )

        self.lead_repository.update.assert_not_called()

        self.event_service.log.assert_called_once()

    # ==========================================================
    # SANS QUOTE
    # ==========================================================

    def test_does_not_search_lead_when_application_has_no_quote(self):
        # Arrange
        application = self.create_application(
            quote_id=None
        )
        payment = self.create_payment()

        self.application_repository.get_by_id.return_value = application
        self.payment_repository.get_by_id.return_value = payment

        # Act
        result = self.use_case.execute(self.dto)

        # Assert
        assert result.assigned_agent_id is None

        self.lead_repository.get_by_quote_id.assert_not_called()
        self.lead_repository.update.assert_not_called()

    # ==========================================================
    # GARANTIE
    # ==========================================================

    def test_activates_vehicle_warranty(self):
        # Arrange
        application = self.create_application()
        payment = self.create_payment()

        self.application_repository.get_by_id.return_value = application
        self.payment_repository.get_by_id.return_value = payment

        # Act
        self.use_case.execute(self.dto)

        # Assert
        self.activate_vehicle_warranty_uc.execute.assert_called_once()

        warranty_dto = (
            self.activate_vehicle_warranty_uc
            .execute
            .call_args
            .args[0]
        )

        assert isinstance(
            warranty_dto,
            ActivateVehicleWarrantyDTO,
        )

        assert warranty_dto.vehicle_id == application.vehicle.id
        assert warranty_dto.mileage == application.vehicle.mileage
        assert warranty_dto.user_id == application.user_id

    # ==========================================================
    # ERREUR GARANTIE
    # ==========================================================

    def test_propagates_warranty_error(self):
        # Arrange
        application = self.create_application()
        payment = self.create_payment()

        self.application_repository.get_by_id.return_value = application
        self.payment_repository.get_by_id.return_value = payment

        self.activate_vehicle_warranty_uc.execute.side_effect = (
            RuntimeError("Warranty error")
        )

        # Act / Assert
        with pytest.raises(
            RuntimeError,
            match="Warranty error",
        ):
            self.use_case.execute(self.dto)

        self.event_service.log.assert_any_call(
            type=EventType.DEPOSIT_PAID,
            application_id=application.id,
            vehicle_id=application.vehicle.id,
            user_id=application.user_id,
            message="Acompte véhicule payé.",
            event_metadata={
                "payment_id": self.dto.payment_id,
                "vehicle_id": application.vehicle.id,
            },
        )

    # ==========================================================
    # ERREUR FINANCEMENT
    # ==========================================================

    def test_propagates_financing_contract_error(self):
        # Arrange
        financing = MagicMock()
        financing.financed_amount = 10000

        application = self.create_application(
            financing=financing
        )
        payment = self.create_payment()

        self.application_repository.get_by_id.return_value = application
        self.payment_repository.get_by_id.return_value = payment

        self.create_financing_contract_uc.execute.side_effect = (
            RuntimeError("Financing contract error")
        )

        # Act / Assert
        with pytest.raises(
            RuntimeError,
            match="Financing contract error",
        ):
            self.use_case.execute(self.dto)

        self.create_subscription_uc.execute.assert_not_called()
        self.create_installments_uc.execute.assert_not_called()

    # ==========================================================
    # ERREUR SUBSCRIPTION
    # ==========================================================

    def test_propagates_subscription_error(self):
        # Arrange
        financing = MagicMock()
        financing.financed_amount = 10000

        application = self.create_application(
            financing=financing
        )
        payment = self.create_payment()

        self.application_repository.get_by_id.return_value = application
        self.payment_repository.get_by_id.return_value = payment

        self.create_financing_contract_uc.execute.return_value = (
            SimpleNamespace(
                contract_id="contract-123"
            )
        )

        self.create_subscription_uc.execute.side_effect = (
            RuntimeError("Subscription error")
        )

        # Act / Assert
        with pytest.raises(
            RuntimeError,
            match="Subscription error",
        ):
            self.use_case.execute(self.dto)

        self.create_installments_uc.execute.assert_not_called()

    # ==========================================================
    # ERREUR INSTALLMENTS
    # ==========================================================

    def test_propagates_installments_error(self):
        # Arrange
        financing = MagicMock()
        financing.financed_amount = 10000

        application = self.create_application(
            financing=financing
        )
        payment = self.create_payment()

        self.application_repository.get_by_id.return_value = application
        self.payment_repository.get_by_id.return_value = payment

        self.create_financing_contract_uc.execute.return_value = (
            SimpleNamespace(
                contract_id="contract-123"
            )
        )

        self.create_installments_uc.execute.side_effect = (
            RuntimeError("Installments error")
        )

        # Act / Assert
        with pytest.raises(
            RuntimeError,
            match="Installments error",
        ):
            self.use_case.execute(self.dto)

        self.create_installments_uc.execute.assert_called_once()

    # ==========================================================
    # PAS DE TRANSACTION DANS CE USE CASE
    # ==========================================================

    def test_does_not_manage_unit_of_work(self):
        """
        CompleteSalePaymentUseCase ne possède pas de UnitOfWork.
        La transaction est gérée par le use case appelant.
        """
        assert not hasattr(self.use_case, "unit_of_work")