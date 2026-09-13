from unittest.mock import Mock

import pytest

from modules.applications.application.dtos.application_id_dto import (
    ApplicationIdDTO,
)
from modules.applications.application.use_cases.cancel_application import (
    CancelApplicationUseCase,
)
from modules.applications.domain.entities.application import Application
from modules.applications.domain.enums import ApplicationStatus, EventType
from modules.applications.domain.exceptions import (
    ApplicationAlreadyCancelled,
    ApplicationNotFound,
    CannotCancelApplication,
)
from modules.applications.domain.policies.cancel_application_policy import (
    CancelApplicationPolicy,
)
from modules.auth.domain.enums import UserRole
from modules.auth.domain.exceptions import Forbidden
from modules.payments.domain.enums import SubscriptionStatus


# ============================================================
# HELPERS
# ============================================================


def make_application(
    *,
    user_id: str = "user-1",
    status: ApplicationStatus = ApplicationStatus.DRAFT,
    financing_contract=None,
    reservation=None,
):
    return Application(
        id="application-1",
        user_id=user_id,
        vehicle_id="vehicle-1",
        status=status,
        financing_contract=financing_contract,
        reservation=reservation,
    )


def make_contract(
    status: SubscriptionStatus = SubscriptionStatus.CANCELLED,
):
    return Mock(subscription_status=status)


def make_reservation():
    return Mock(id="reservation-1")


# ============================================================
# POLICY
# ============================================================


class TestCancelApplicationPolicy:

    def test_cancelled_application_cannot_be_cancelled(self):
        application = make_application(
            status=ApplicationStatus.CANCELLED
        )

        assert CancelApplicationPolicy.can_cancel(application) is False

    def test_cancelled_application_raises_application_already_cancelled(self):
        application = make_application(
            status=ApplicationStatus.CANCELLED
        )

        with pytest.raises(ApplicationAlreadyCancelled):
            CancelApplicationPolicy.validate(application)

    @pytest.mark.parametrize(
        "status",
        [
            ApplicationStatus.PAID,
            ApplicationStatus.COMPLETED,
        ],
    )
    def test_paid_or_completed_application_cannot_be_cancelled(
        self,
        status,
    ):
        application = make_application(status=status)

        assert CancelApplicationPolicy.can_cancel(application) is False

        with pytest.raises(CannotCancelApplication):
            CancelApplicationPolicy.validate(application)

    @pytest.mark.parametrize(
        "subscription_status",
        [
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.COMPLETED,
        ],
    )
    def test_application_with_active_or_completed_contract_cannot_be_cancelled(
        self,
        subscription_status,
    ):
        contract = make_contract(subscription_status)

        application = make_application(
            financing_contract=contract
        )

        assert CancelApplicationPolicy.can_cancel(application) is False

        with pytest.raises(CannotCancelApplication):
            CancelApplicationPolicy.validate(application)

    def test_application_with_cancelled_contract_can_be_cancelled(self):
        contract = make_contract(
            SubscriptionStatus.CANCELLED
        )

        application = make_application(
            financing_contract=contract
        )

        assert CancelApplicationPolicy.can_cancel(application) is True

        CancelApplicationPolicy.validate(application)

    def test_application_without_contract_can_be_cancelled(self):
        application = make_application()

        assert application.financing_contract is None
        assert CancelApplicationPolicy.can_cancel(application) is True

        CancelApplicationPolicy.validate(application)

    def test_draft_application_can_be_cancelled(self):
        application = make_application(
            status=ApplicationStatus.DRAFT
        )

        assert CancelApplicationPolicy.can_cancel(application) is True

        CancelApplicationPolicy.validate(application)


# ============================================================
# USE CASE
# ============================================================


class TestCancelApplicationUseCase:

    @pytest.fixture
    def application_repository(self):
        return Mock()

    @pytest.fixture
    def financing_contract_repository(self):
        return Mock()

    @pytest.fixture
    def event_service(self):
        return Mock()

    @pytest.fixture
    def cancel_reservation_uc(self):
        return Mock()

    @pytest.fixture
    def unit_of_work(self):
        return Mock()

    @pytest.fixture
    def use_case(
        self,
        application_repository,
        financing_contract_repository,
        event_service,
        cancel_reservation_uc,
        unit_of_work,
    ):
        return CancelApplicationUseCase(
            application_repository=application_repository,
            financing_contract_repository=financing_contract_repository,
            event_service=event_service,
            cancel_reservation_uc=cancel_reservation_uc,
            unit_of_work=unit_of_work,
        )

    @pytest.fixture
    def dto(self):
        return ApplicationIdDTO(
            application_id="application-1"
        )

    # --------------------------------------------------------
    # NOT FOUND
    # --------------------------------------------------------

    def test_application_not_found(
        self,
        use_case,
        application_repository,
        unit_of_work,
        dto,
    ):
        application_repository.get_by_id.return_value = None

        with pytest.raises(ApplicationNotFound):
            use_case.execute(
                dto=dto,
                role=UserRole.CLIENT,
                user_id="user-1",
            )

        application_repository.get_by_id.assert_called_once_with(
            "application-1"
        )

        unit_of_work.rollback.assert_called_once()
        unit_of_work.commit.assert_not_called()

    # --------------------------------------------------------
    # AUTHORIZATION
    # --------------------------------------------------------

    def test_client_cannot_cancel_another_users_application(
        self,
        use_case,
        application_repository,
        unit_of_work,
        dto,
    ):
        application = make_application(
            user_id="owner-1"
        )

        application_repository.get_by_id.return_value = application

        with pytest.raises(Forbidden):
            use_case.execute(
                dto=dto,
                role=UserRole.CLIENT,
                user_id="another-user",
            )

        unit_of_work.rollback.assert_called_once()
        unit_of_work.commit.assert_not_called()

    def test_admin_can_cancel_another_users_application(
        self,
        use_case,
        application_repository,
        event_service,
        unit_of_work,
        dto,
    ):
        application = make_application(
            user_id="owner-1"
        )

        application_repository.get_by_id.return_value = application

        result = use_case.execute(
            dto=dto,
            role=UserRole.ADMIN,
            user_id="admin-1",
        )

        assert result is application
        assert application.status == ApplicationStatus.CANCELLED
        assert application.previous_status == ApplicationStatus.DRAFT

        unit_of_work.commit.assert_called_once()

    # --------------------------------------------------------
    # POLICY
    # --------------------------------------------------------

    def test_already_cancelled_application_is_rejected(
        self,
        use_case,
        application_repository,
        unit_of_work,
        dto,
    ):
        application = make_application(
            status=ApplicationStatus.CANCELLED
        )

        application_repository.get_by_id.return_value = application

        with pytest.raises(ApplicationAlreadyCancelled):
            use_case.execute(
                dto=dto,
                role=UserRole.CLIENT,
                user_id="user-1",
            )

        unit_of_work.rollback.assert_called_once()
        unit_of_work.commit.assert_not_called()

    @pytest.mark.parametrize(
        "status",
        [
            ApplicationStatus.PAID,
            ApplicationStatus.COMPLETED,
        ],
    )
    def test_forbidden_status_is_rejected(
        self,
        status,
        use_case,
        application_repository,
        unit_of_work,
        dto,
    ):
        application = make_application(
            status=status
        )

        application_repository.get_by_id.return_value = application

        with pytest.raises(CannotCancelApplication):
            use_case.execute(
                dto=dto,
                role=UserRole.CLIENT,
                user_id="user-1",
            )

        unit_of_work.rollback.assert_called_once()
        unit_of_work.commit.assert_not_called()

    def test_active_financing_contract_prevents_cancellation(
        self,
        use_case,
        application_repository,
        unit_of_work,
        dto,
    ):
        contract = make_contract(
            SubscriptionStatus.ACTIVE
        )

        application = make_application(
            financing_contract=contract
        )

        application_repository.get_by_id.return_value = application

        with pytest.raises(CannotCancelApplication):
            use_case.execute(
                dto=dto,
                role=UserRole.CLIENT,
                user_id="user-1",
            )

        unit_of_work.rollback.assert_called_once()
        unit_of_work.commit.assert_not_called()

    # --------------------------------------------------------
    # FINANCING CONTRACT
    # --------------------------------------------------------

    def test_financing_contract_is_cancelled(
        self,
        use_case,
        application_repository,
        financing_contract_repository,
        unit_of_work,
        dto,
    ):
        contract = make_contract(
            SubscriptionStatus.CANCELLED
        )

        application = make_application(
            financing_contract=contract
        )

        application_repository.get_by_id.return_value = application

        use_case.execute(
            dto=dto,
            role=UserRole.CLIENT,
            user_id="user-1",
        )

        assert (
            contract.subscription_status
            == SubscriptionStatus.CANCELLED
        )

        financing_contract_repository.update.assert_called_once_with(
            contract
        )

    def test_financing_contract_is_not_updated_when_absent(
        self,
        use_case,
        application_repository,
        financing_contract_repository,
        dto,
    ):
        application = make_application()

        application_repository.get_by_id.return_value = application

        use_case.execute(
            dto=dto,
            role=UserRole.CLIENT,
            user_id="user-1",
        )

        financing_contract_repository.update.assert_not_called()

    # --------------------------------------------------------
    # RESERVATION
    # --------------------------------------------------------

    def test_reservation_is_cancelled(
        self,
        use_case,
        application_repository,
        cancel_reservation_uc,
        dto,
    ):
        reservation = make_reservation()

        application = make_application(
            reservation=reservation
        )

        application_repository.get_by_id.return_value = application

        use_case.execute(
            dto=dto,
            role=UserRole.CLIENT,
            user_id="user-1",
        )

        cancel_reservation_uc.execute.assert_called_once_with(
            reservation_id="reservation-1",
            role=UserRole.CLIENT,
            user_id="user-1",
        )

    def test_reservation_is_not_cancelled_when_absent(
        self,
        use_case,
        application_repository,
        cancel_reservation_uc,
        dto,
    ):
        application = make_application(
            reservation=None
        )

        application_repository.get_by_id.return_value = application

        use_case.execute(
            dto=dto,
            role=UserRole.CLIENT,
            user_id="user-1",
        )

        cancel_reservation_uc.execute.assert_not_called()

    # --------------------------------------------------------
    # APPLICATION STATUS
    # --------------------------------------------------------

    def test_application_status_is_changed_to_cancelled(
        self,
        use_case,
        application_repository,
        dto,
    ):
        application = make_application(
            status=ApplicationStatus.DRAFT
        )

        application_repository.get_by_id.return_value = application

        result = use_case.execute(
            dto=dto,
            role=UserRole.CLIENT,
            user_id="user-1",
        )

        assert result is application
        assert application.previous_status == ApplicationStatus.DRAFT
        assert application.status == ApplicationStatus.CANCELLED

    # --------------------------------------------------------
    # APPLICATION REPOSITORY
    # --------------------------------------------------------

    def test_application_is_updated(
        self,
        use_case,
        application_repository,
        dto,
    ):
        application = make_application()

        application_repository.get_by_id.return_value = application

        use_case.execute(
            dto=dto,
            role=UserRole.CLIENT,
            user_id="user-1",
        )

        application_repository.update.assert_called_once_with(
            application
        )

    # --------------------------------------------------------
    # EVENT
    # --------------------------------------------------------

    def test_cancellation_event_is_created_for_client(
        self,
        use_case,
        application_repository,
        event_service,
        unit_of_work,
        dto,
    ):
        application = make_application()

        application_repository.get_by_id.return_value = application

        use_case.execute(
            dto=dto,
            role=UserRole.CLIENT,
            user_id="user-1",
        )

        event_service.log.assert_called_once_with(
            application_id="application-1",
            user_id="user-1",
            vehicle_id="vehicle-1",
            type=EventType.APPLICATION_CANCELLED,
            message="Dossier annulé par client.",
            event_metadata={
                "role": UserRole.CLIENT,
            },
        )

        unit_of_work.commit.assert_called_once()

    def test_cancellation_event_is_created_for_admin(
        self,
        use_case,
        application_repository,
        event_service,
        dto,
    ):
        application = make_application(
            user_id="client-1"
        )

        application_repository.get_by_id.return_value = application

        use_case.execute(
            dto=dto,
            role=UserRole.ADMIN,
            user_id="admin-1",
        )

        event_service.log.assert_called_once_with(
            application_id="application-1",
            user_id="admin-1",
            vehicle_id="vehicle-1",
            type=EventType.APPLICATION_CANCELLED,
            message="Dossier annulé par administrateur.",
            event_metadata={
                "role": UserRole.ADMIN,
            },
        )

    # --------------------------------------------------------
    # TRANSACTION / ROLLBACK
    # --------------------------------------------------------

    def test_financing_contract_update_error_rolls_back(
        self,
        use_case,
        application_repository,
        financing_contract_repository,
        unit_of_work,
        dto,
    ):
        contract = make_contract()

        application = make_application(
            financing_contract=contract
        )

        application_repository.get_by_id.return_value = application

        financing_contract_repository.update.side_effect = RuntimeError(
            "database error"
        )

        with pytest.raises(RuntimeError, match="database error"):
            use_case.execute(
                dto=dto,
                role=UserRole.CLIENT,
                user_id="user-1",
            )

        unit_of_work.rollback.assert_called_once()
        unit_of_work.commit.assert_not_called()

    def test_reservation_cancellation_error_rolls_back(
        self,
        use_case,
        application_repository,
        cancel_reservation_uc,
        unit_of_work,
        dto,
    ):
        reservation = make_reservation()

        application = make_application(
            reservation=reservation
        )

        application_repository.get_by_id.return_value = application

        cancel_reservation_uc.execute.side_effect = RuntimeError(
            "reservation error"
        )

        with pytest.raises(RuntimeError, match="reservation error"):
            use_case.execute(
                dto=dto,
                role=UserRole.CLIENT,
                user_id="user-1",
            )

        unit_of_work.rollback.assert_called_once()
        unit_of_work.commit.assert_not_called()

    def test_application_update_error_rolls_back(
        self,
        use_case,
        application_repository,
        unit_of_work,
        dto,
    ):
        application = make_application()

        application_repository.get_by_id.return_value = application

        application_repository.update.side_effect = RuntimeError(
            "application update error"
        )

        with pytest.raises(
            RuntimeError,
            match="application update error",
        ):
            use_case.execute(
                dto=dto,
                role=UserRole.CLIENT,
                user_id="user-1",
            )

        unit_of_work.rollback.assert_called_once()
        unit_of_work.commit.assert_not_called()

    def test_event_error_rolls_back(
        self,
        use_case,
        application_repository,
        event_service,
        unit_of_work,
        dto,
    ):
        application = make_application()

        application_repository.get_by_id.return_value = application

        event_service.log.side_effect = RuntimeError(
            "event error"
        )

        with pytest.raises(RuntimeError, match="event error"):
            use_case.execute(
                dto=dto,
                role=UserRole.CLIENT,
                user_id="user-1",
            )

        unit_of_work.rollback.assert_called_once()
        unit_of_work.commit.assert_not_called()

    def test_commit_error_rolls_back(
        self,
        use_case,
        application_repository,
        unit_of_work,
        dto,
    ):
        application = make_application()

        application_repository.get_by_id.return_value = application

        unit_of_work.commit.side_effect = RuntimeError(
            "commit error"
        )

        with pytest.raises(RuntimeError, match="commit error"):
            use_case.execute(
                dto=dto,
                role=UserRole.CLIENT,
                user_id="user-1",
            )

        unit_of_work.commit.assert_called_once()
        unit_of_work.rollback.assert_called_once()
