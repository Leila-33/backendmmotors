from types import SimpleNamespace
from unittest.mock import MagicMock, AsyncMock

import pytest

from modules.applications.domain.enums import EventType
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.payments.application.dtos.complete_rental_payment_dto import (
    CompleteRentalPaymentDTO,
)
from modules.payments.application.dtos.complete_sale_payment_dto import (
    CompleteSalePaymentDTO,
)
from modules.payments.application.dtos.handle_payment_success_dto import (
    HandlePaymentSuccessDTO,
)
from modules.payments.application.use_cases.handle_payment_success import (
    HandlePaymentSuccessUseCase,
)
from modules.payments.domain.enums import PaymentStatus
from modules.payments.domain.exceptions import (
    PaymentInvalid,
    PaymentNotFound,
)
from modules.payments.application.results.handle_payment_success_result import (
    HandlePaymentSuccessResult,
)
from modules.vehicles.domain.enums import VehicleType


class TestHandlePaymentSuccessUseCase:

    def setup_method(self):
        self.payment_repository = MagicMock()
        self.application_repository = MagicMock()

        self.complete_sale_payment_uc = MagicMock()
        self.complete_rental_payment_uc = MagicMock()

        self.sales_dashboard_repository = MagicMock()

        self.notification_service = MagicMock()
        self.notification_service.send_update = AsyncMock()

        self.event_service = MagicMock()
        self.stripe_service = MagicMock()
        self.unit_of_work = MagicMock()

        self.use_case = HandlePaymentSuccessUseCase(
            payment_repository=self.payment_repository,
            application_repository=self.application_repository,
            complete_sale_payment_uc=self.complete_sale_payment_uc,
            complete_rental_payment_uc=self.complete_rental_payment_uc,
            sales_dashboard_repository=self.sales_dashboard_repository,
            notification_service=self.notification_service,
            event_service=self.event_service,
            stripe_service=self.stripe_service,
            unit_of_work=self.unit_of_work,
        )

        self.dto = HandlePaymentSuccessDTO(
            stripe_session_id="cs_test_123",
            stripe_payment_intent_id="pi_test_123",
        )

    # ==========================================================
    # HELPERS
    # ==========================================================

    def create_payment(
        self,
        status=PaymentStatus.PENDING,
        stripe_customer_id="cus_test_123",
    ):
        payment = MagicMock()

        payment.id = "payment-123"
        payment.application_id = "application-123"
        payment.status = status
        payment.amount = 15000
        payment.stripe_customer_id = stripe_customer_id
        payment.stripe_payment_intent_id = None
        payment.paid_at = None

        return payment

    def create_application(
        self,
        vehicle_type=VehicleType.SALE,
        assigned_agent_id=None,
    ):
        vehicle = MagicMock()

        vehicle.id = "vehicle-123"
        vehicle.type = vehicle_type

        application = MagicMock()

        application.id = "application-123"
        application.user_id = "customer-123"
        application.vehicle = vehicle

        if assigned_agent_id is not None:
            application.assigned_agent_id = assigned_agent_id

        return application

    # ==========================================================
    # SUCCÈS - VENTE
    # ==========================================================

    @pytest.mark.asyncio
    async def test_processes_successful_sale_payment(self):
        # Arrange
        payment = self.create_payment()
        application = self.create_application(
            vehicle_type=VehicleType.SALE
        )

        sale_result = SimpleNamespace(
            assigned_agent_id="agent-123"
        )

        self.payment_repository.get_by_session_id.return_value = payment
        self.application_repository.get_by_id.return_value = application

        self.complete_sale_payment_uc.execute.return_value = sale_result

        self.sales_dashboard_repository.count_my_leads.return_value = 4

        # Act
        result = await self.use_case.execute(self.dto)

        # Assert
        assert isinstance(result, HandlePaymentSuccessResult)

        assert result.payment_id == payment.id
        assert result.status == PaymentStatus.PAID.value
        assert result.vehicle_type == VehicleType.SALE.value
        assert result.application_id == application.id
        assert result.message == "Paiement traité avec succès"

        self.payment_repository.get_by_session_id.assert_called_once_with(
            self.dto.stripe_session_id
        )

        self.application_repository.get_by_id.assert_called_once_with(
            payment.application_id
        )

        self.stripe_service.set_customer_default_payment_method.assert_called_once_with(
            customer_id=payment.stripe_customer_id,
            payment_intent_id=self.dto.stripe_payment_intent_id,
        )

        assert payment.stripe_payment_intent_id == (
            self.dto.stripe_payment_intent_id
        )

        assert payment.status == PaymentStatus.PAID
        assert payment.paid_at is not None

        self.payment_repository.update.assert_called_once_with(
            payment
        )

        self.complete_sale_payment_uc.execute.assert_called_once()

        sale_dto = (
            self.complete_sale_payment_uc
            .execute
            .call_args
            .args[0]
        )

        assert isinstance(
            sale_dto,
            CompleteSalePaymentDTO,
        )

        assert sale_dto.application_id == application.id
        assert sale_dto.payment_id == payment.id

        self.complete_rental_payment_uc.execute.assert_not_called()

        self.event_service.log.assert_called_once_with(
            type=EventType.PAYMENT_SUCCEEDED,
            message="Paiement confirmé",
            application_id=application.id,
            user_id=application.user_id,
            vehicle_id=application.vehicle.id,
            event_metadata={
                "payment_id": payment.id,
                "amount": payment.amount,
                "vehicle_type": VehicleType.SALE.value,
                "stripe_session_id": self.dto.stripe_session_id,
                "stripe_customer_id": payment.stripe_customer_id,
                "stripe_payment_intent_id": (
                    self.dto.stripe_payment_intent_id
                ),
            },
        )

        self.unit_of_work.commit.assert_called_once()
        self.unit_of_work.rollback.assert_not_called()

    # ==========================================================
    # SUCCÈS - LOCATION
    # ==========================================================

    @pytest.mark.asyncio
    async def test_processes_successful_rental_payment(self):
        # Arrange
        payment = self.create_payment()

        application = self.create_application(
            vehicle_type=VehicleType.RENT
        )

        self.payment_repository.get_by_session_id.return_value = payment
        self.application_repository.get_by_id.return_value = application

        # Act
        result = await self.use_case.execute(self.dto)

        # Assert
        assert result.payment_id == payment.id
        assert result.status == PaymentStatus.PAID.value
        assert result.vehicle_type == VehicleType.RENT.value
        assert result.application_id == application.id

        self.complete_rental_payment_uc.execute.assert_called_once()

        rental_dto = (
            self.complete_rental_payment_uc
            .execute
            .call_args
            .args[0]
        )

        assert isinstance(
            rental_dto,
            CompleteRentalPaymentDTO,
        )

        assert rental_dto.application_id == application.id
        assert rental_dto.payment_id == payment.id

        self.complete_sale_payment_uc.execute.assert_not_called()

        self.unit_of_work.commit.assert_called_once()

    # ==========================================================
    # PAYMENT INTROUVABLE
    # ==========================================================

    @pytest.mark.asyncio
    async def test_raises_payment_not_found_when_payment_does_not_exist(self):
        # Arrange
        self.payment_repository.get_by_session_id.return_value = None

        # Act / Assert
        with pytest.raises(PaymentNotFound):
            await self.use_case.execute(self.dto)

        self.payment_repository.get_by_session_id.assert_called_once_with(
            self.dto.stripe_session_id
        )

        self.application_repository.get_by_id.assert_not_called()

        self.unit_of_work.commit.assert_not_called()
        self.unit_of_work.rollback.assert_called_once()

    # ==========================================================
    # APPLICATION INTROUVABLE
    # ==========================================================

    @pytest.mark.asyncio
    async def test_raises_application_not_found_when_application_does_not_exist(
        self,
    ):
        # Arrange
        payment = self.create_payment()

        self.payment_repository.get_by_session_id.return_value = payment
        self.application_repository.get_by_id.return_value = None

        # Act / Assert
        with pytest.raises(ApplicationNotFound):
            await self.use_case.execute(self.dto)

        self.application_repository.get_by_id.assert_called_once_with(
            payment.application_id
        )

        self.unit_of_work.commit.assert_not_called()
        self.unit_of_work.rollback.assert_called_once()

    # ==========================================================
    # IDEMPOTENCE
    # ==========================================================

    @pytest.mark.asyncio
    async def test_returns_success_without_reprocessing_already_paid_payment(
        self,
    ):
        # Arrange
        payment = self.create_payment(
            status=PaymentStatus.PAID
        )

        application = self.create_application(
            vehicle_type=VehicleType.SALE
        )

        self.payment_repository.get_by_session_id.return_value = payment
        self.application_repository.get_by_id.return_value = application

        # Act
        result = await self.use_case.execute(self.dto)

        # Assert
        assert result.payment_id == payment.id
        assert result.status == PaymentStatus.PAID.value
        assert result.vehicle_type == VehicleType.SALE.value
        assert result.application_id == application.id
        assert result.message == "Paiement déjà traité"

        self.payment_repository.update.assert_not_called()

        self.stripe_service.set_customer_default_payment_method.assert_not_called()

        self.complete_sale_payment_uc.execute.assert_not_called()
        self.complete_rental_payment_uc.execute.assert_not_called()

        self.event_service.log.assert_not_called()

        self.unit_of_work.commit.assert_not_called()
        self.unit_of_work.rollback.assert_not_called()

        self.notification_service.send_update.assert_not_awaited()

    # ==========================================================
    # CUSTOMER STRIPE ABSENT
    # ==========================================================

    @pytest.mark.asyncio
    async def test_raises_payment_invalid_when_stripe_customer_is_missing(
        self,
    ):
        # Arrange
        payment = self.create_payment(
            stripe_customer_id=None
        )

        application = self.create_application()

        self.payment_repository.get_by_session_id.return_value = payment
        self.application_repository.get_by_id.return_value = application

        # Act / Assert
        with pytest.raises(
            PaymentInvalid,
            match="Customer Stripe absent du paiement.",
        ):
            await self.use_case.execute(self.dto)

        self.stripe_service.set_customer_default_payment_method.assert_not_called()

        self.payment_repository.update.assert_not_called()

        self.complete_sale_payment_uc.execute.assert_not_called()
        self.complete_rental_payment_uc.execute.assert_not_called()

        self.event_service.log.assert_not_called()

        self.unit_of_work.commit.assert_not_called()
        self.unit_of_work.rollback.assert_called_once()

    # ==========================================================
    # PAYMENT INTENT ABSENT
    # ==========================================================

    @pytest.mark.asyncio
    async def test_raises_payment_invalid_when_payment_intent_is_missing(
        self,
    ):
        # Arrange
        payment = self.create_payment()

        application = self.create_application()

        dto = HandlePaymentSuccessDTO(
            stripe_session_id="cs_test_123",
            stripe_payment_intent_id=None,
        )

        self.payment_repository.get_by_session_id.return_value = payment
        self.application_repository.get_by_id.return_value = application

        # Act / Assert
        with pytest.raises(
            PaymentInvalid,
            match="PaymentIntent Stripe absent du paiement.",
        ):
            await self.use_case.execute(dto)

        self.stripe_service.set_customer_default_payment_method.assert_not_called()

        self.payment_repository.update.assert_not_called()

        self.complete_sale_payment_uc.execute.assert_not_called()
        self.complete_rental_payment_uc.execute.assert_not_called()

        self.event_service.log.assert_not_called()

        self.unit_of_work.commit.assert_not_called()
        self.unit_of_work.rollback.assert_called_once()

    # ==========================================================
    # STRIPE DEFAULT PAYMENT METHOD
    # ==========================================================

    @pytest.mark.asyncio
    async def test_sets_customer_default_payment_method(self):
        # Arrange
        payment = self.create_payment()

        application = self.create_application(
            vehicle_type=VehicleType.RENT
        )

        self.payment_repository.get_by_session_id.return_value = payment
        self.application_repository.get_by_id.return_value = application

        # Act
        await self.use_case.execute(self.dto)

        # Assert
        self.stripe_service.set_customer_default_payment_method.assert_called_once_with(
            customer_id="cus_test_123",
            payment_intent_id="pi_test_123",
        )

    # ==========================================================
    # PAYMENT MARKED PAID
    # ==========================================================

    @pytest.mark.asyncio
    async def test_marks_payment_as_paid(self):
        # Arrange
        payment = self.create_payment()

        application = self.create_application(
            vehicle_type=VehicleType.RENT
        )

        self.payment_repository.get_by_session_id.return_value = payment
        self.application_repository.get_by_id.return_value = application

        # Act
        await self.use_case.execute(self.dto)

        # Assert
        assert payment.status == PaymentStatus.PAID
        assert payment.paid_at is not None

        assert payment.paid_at.tzinfo is not None
        assert payment.paid_at.utcoffset() is not None

        self.payment_repository.update.assert_called_once_with(
            payment
        )

    # ==========================================================
    # EVENT PAYMENT SUCCESS
    # ==========================================================

    @pytest.mark.asyncio
    async def test_logs_payment_success_event(self):
        # Arrange
        payment = self.create_payment()

        application = self.create_application(
            vehicle_type=VehicleType.RENT
        )

        self.payment_repository.get_by_session_id.return_value = payment
        self.application_repository.get_by_id.return_value = application

        # Act
        await self.use_case.execute(self.dto)

        # Assert
        self.event_service.log.assert_called_once_with(
            type=EventType.PAYMENT_SUCCEEDED,
            message="Paiement confirmé",
            application_id=application.id,
            user_id=application.user_id,
            vehicle_id=application.vehicle.id,
            event_metadata={
                "payment_id": payment.id,
                "amount": payment.amount,
                "vehicle_type": VehicleType.RENT.value,
                "stripe_session_id": self.dto.stripe_session_id,
                "stripe_customer_id": payment.stripe_customer_id,
                "stripe_payment_intent_id": (
                    self.dto.stripe_payment_intent_id
                ),
            },
        )

    # ==========================================================
    # NOTIFICATION AGENT - VENTE
    # ==========================================================

    @pytest.mark.asyncio
    async def test_updates_sales_agent_leads_count_after_sale(self):
        # Arrange
        payment = self.create_payment()

        application = self.create_application(
            vehicle_type=VehicleType.SALE
        )

        sale_result = SimpleNamespace(
            assigned_agent_id="agent-123"
        )

        self.payment_repository.get_by_session_id.return_value = payment
        self.application_repository.get_by_id.return_value = application

        self.complete_sale_payment_uc.execute.return_value = sale_result

        self.sales_dashboard_repository.count_my_leads.return_value = 8

        # Act
        await self.use_case.execute(self.dto)

        # Assert
        self.sales_dashboard_repository.count_my_leads.assert_called_once_with(
            agent_id="agent-123"
        )

        self.notification_service.send_update.assert_awaited_once_with(
            user_id="agent-123",
            payload={
                "type": "MY_LEADS_UPDATED",
                "count": 8,
            },
        )

    # ==========================================================
    # PAS DE NOTIFICATION SI PAS D'AGENT
    # ==========================================================

    @pytest.mark.asyncio
    async def test_does_not_update_agent_count_when_sale_has_no_assigned_agent(
        self,
    ):
        # Arrange
        payment = self.create_payment()

        application = self.create_application(
            vehicle_type=VehicleType.SALE
        )

        sale_result = SimpleNamespace(
            assigned_agent_id=None
        )

        self.payment_repository.get_by_session_id.return_value = payment
        self.application_repository.get_by_id.return_value = application

        self.complete_sale_payment_uc.execute.return_value = sale_result

        # Act
        await self.use_case.execute(self.dto)

        # Assert
        self.sales_dashboard_repository.count_my_leads.assert_not_called()

        self.notification_service.send_update.assert_not_awaited()

    # ==========================================================
    # PAS DE NOTIFICATION AGENT POUR UNE LOCATION
    # ==========================================================

    @pytest.mark.asyncio
    async def test_does_not_update_sales_agent_count_for_rental(self):
        # Arrange
        payment = self.create_payment()

        application = self.create_application(
            vehicle_type=VehicleType.RENT
        )

        self.payment_repository.get_by_session_id.return_value = payment
        self.application_repository.get_by_id.return_value = application

        # Act
        await self.use_case.execute(self.dto)

        # Assert
        self.sales_dashboard_repository.count_my_leads.assert_not_called()

        self.notification_service.send_update.assert_not_awaited()

    # ==========================================================
    # ERREUR STRIPE
    # ==========================================================

    @pytest.mark.asyncio
    async def test_rolls_back_when_stripe_service_fails(self):
        # Arrange
        payment = self.create_payment()

        application = self.create_application()

        self.payment_repository.get_by_session_id.return_value = payment
        self.application_repository.get_by_id.return_value = application

        self.stripe_service.set_customer_default_payment_method.side_effect = (
            RuntimeError("Stripe error")
        )

        # Act / Assert
        with pytest.raises(RuntimeError, match="Stripe error"):
            await self.use_case.execute(self.dto)

        self.payment_repository.update.assert_not_called()

        self.complete_sale_payment_uc.execute.assert_not_called()
        self.complete_rental_payment_uc.execute.assert_not_called()

        self.event_service.log.assert_not_called()

        self.unit_of_work.commit.assert_not_called()
        self.unit_of_work.rollback.assert_called_once()

    # ==========================================================
    # ERREUR COMPLETION VENTE
    # ==========================================================

    @pytest.mark.asyncio
    async def test_rolls_back_when_sale_completion_fails(self):
        # Arrange
        payment = self.create_payment()

        application = self.create_application(
            vehicle_type=VehicleType.SALE
        )

        self.payment_repository.get_by_session_id.return_value = payment
        self.application_repository.get_by_id.return_value = application

        self.complete_sale_payment_uc.execute.side_effect = RuntimeError(
            "Sale completion error"
        )

        # Act / Assert
        with pytest.raises(
            RuntimeError,
            match="Sale completion error",
        ):
            await self.use_case.execute(self.dto)

        self.payment_repository.update.assert_called_once_with(
            payment
        )

        self.event_service.log.assert_not_called()

        self.unit_of_work.commit.assert_not_called()
        self.unit_of_work.rollback.assert_called_once()

    # ==========================================================
    # ERREUR COMPLETION LOCATION
    # ==========================================================

    @pytest.mark.asyncio
    async def test_rolls_back_when_rental_completion_fails(self):
        # Arrange
        payment = self.create_payment()

        application = self.create_application(
            vehicle_type=VehicleType.RENT
        )

        self.payment_repository.get_by_session_id.return_value = payment
        self.application_repository.get_by_id.return_value = application

        self.complete_rental_payment_uc.execute.side_effect = RuntimeError(
            "Rental completion error"
        )

        # Act / Assert
        with pytest.raises(
            RuntimeError,
            match="Rental completion error",
        ):
            await self.use_case.execute(self.dto)

        self.payment_repository.update.assert_called_once_with(
            payment
        )

        self.event_service.log.assert_not_called()

        self.unit_of_work.commit.assert_not_called()
        self.unit_of_work.rollback.assert_called_once()

    # ==========================================================
    # ERREUR EVENT
    # ==========================================================

    @pytest.mark.asyncio
    async def test_rolls_back_when_event_logging_fails(self):
        # Arrange
        payment = self.create_payment()

        application = self.create_application(
            vehicle_type=VehicleType.RENT
        )

        self.payment_repository.get_by_session_id.return_value = payment
        self.application_repository.get_by_id.return_value = application

        self.event_service.log.side_effect = RuntimeError(
            "Event error"
        )

        # Act / Assert
        with pytest.raises(RuntimeError, match="Event error"):
            await self.use_case.execute(self.dto)

        self.payment_repository.update.assert_called_once_with(
            payment
        )

        self.unit_of_work.commit.assert_not_called()
        self.unit_of_work.rollback.assert_called_once()

    # ==========================================================
    # ERREUR COMMIT
    # ==========================================================

    @pytest.mark.asyncio
    async def test_rolls_back_when_commit_fails(self):
        # Arrange
        payment = self.create_payment()

        application = self.create_application(
            vehicle_type=VehicleType.RENT
        )

        self.payment_repository.get_by_session_id.return_value = payment
        self.application_repository.get_by_id.return_value = application

        self.unit_of_work.commit.side_effect = RuntimeError(
            "Commit error"
        )

        # Act / Assert
        with pytest.raises(RuntimeError, match="Commit error"):
            await self.use_case.execute(self.dto)

        self.unit_of_work.commit.assert_called_once()
        self.unit_of_work.rollback.assert_called_once()

        self.notification_service.send_update.assert_not_awaited()

    # ==========================================================
    # ERREUR NOTIFICATION APRÈS COMMIT
    # ==========================================================

    @pytest.mark.asyncio
    async def test_rolls_back_when_agent_notification_fails_after_commit(
        self,
    ):
        # Arrange
        payment = self.create_payment()

        application = self.create_application(
            vehicle_type=VehicleType.SALE
        )

        sale_result = SimpleNamespace(
            assigned_agent_id="agent-123"
        )

        self.payment_repository.get_by_session_id.return_value = payment
        self.application_repository.get_by_id.return_value = application

        self.complete_sale_payment_uc.execute.return_value = sale_result

        self.sales_dashboard_repository.count_my_leads.return_value = 3

        self.notification_service.send_update.side_effect = RuntimeError(
            "Notification error"
        )

        # Act / Assert
        with pytest.raises(
            RuntimeError,
            match="Notification error",
        ):
            await self.use_case.execute(self.dto)

        self.unit_of_work.commit.assert_called_once()
        self.unit_of_work.rollback.assert_called_once()