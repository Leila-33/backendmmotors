from unittest.mock import Mock

import pytest

from modules.applications.application.dtos.application_id_dto import (
    ApplicationIdDTO,
)
from modules.applications.application.use_cases.admin.restore_cancelled_application import (
    RestoreCancelledApplicationUseCase,
)
from modules.applications.domain.entities.application import Application
from modules.applications.domain.enums import ApplicationStatus
from modules.applications.domain.exceptions import (
    ApplicationNotFound,
    CannotRestoreApplication,
)
from modules.auth.domain.enums import UserRole
from modules.reservations.domain.enums import ReservationStatus


# ============================================================
# HELPERS
# ============================================================


def make_current_admin(
    *,
    user_id: str = "admin-1",
):
    """
    Mock volontairement utilisé ici afin de ne pas dépendre
    du constructeur exact de l'entité User.
    """
    return Mock(
        id=user_id,
        role=UserRole.ADMIN,
    )


def make_reservation(
    *,
    reservation_id: str = "reservation-1",
    status: ReservationStatus = ReservationStatus.CANCELLED,
):
    return Mock(
        id=reservation_id,
        status=status,
    )


def make_application(
    *,
    application_id: str = "application-1",
    user_id: str = "user-1",
    vehicle_id: str = "vehicle-1",
    status: ApplicationStatus = ApplicationStatus.CANCELLED,
    previous_status: ApplicationStatus | None = ApplicationStatus.DRAFT,
    reservation=None,
):
    return Application(
        id=application_id,
        user_id=user_id,
        vehicle_id=vehicle_id,
        status=status,
        previous_status=previous_status,
        reservation=reservation,
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def application_repository():
    return Mock()


@pytest.fixture
def reservation_repository():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def restore_application_service():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    application_repository,
    reservation_repository,
    event_service,
    restore_application_service,
    unit_of_work,
):
    return RestoreCancelledApplicationUseCase(
        application_repository=application_repository,
        reservation_repository=reservation_repository,
        event_service=event_service,
        restore_application_service=restore_application_service,
        unit_of_work=unit_of_work,
    )


@pytest.fixture
def dto():
    return ApplicationIdDTO(
        application_id="application-1",
    )


@pytest.fixture
def current_admin():
    return make_current_admin()


# ============================================================
# APPLICATION NOT FOUND
# ============================================================


def test_application_not_found(
    use_case,
    application_repository,
    unit_of_work,
    dto,
    current_admin,
):
    application_repository.get_by_id.return_value = None

    with pytest.raises(ApplicationNotFound):
        use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    application_repository.get_by_id.assert_called_once_with(
        "application-1",
    )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# POLICY
# ============================================================


def test_non_cancelled_application_cannot_be_restored(
    use_case,
    application_repository,
    restore_application_service,
    unit_of_work,
    dto,
    current_admin,
):
    application = make_application(
        status=ApplicationStatus.DRAFT,
        previous_status=ApplicationStatus.CANCELLED,
    )

    application_repository.get_by_id.return_value = application

    with pytest.raises(CannotRestoreApplication):
        use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    restore_application_service.validate_rental.assert_not_called()
    application_repository.update.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_application_without_previous_status_cannot_be_restored(
    use_case,
    application_repository,
    restore_application_service,
    unit_of_work,
    dto,
    current_admin,
):
    application = make_application(
        status=ApplicationStatus.CANCELLED,
        previous_status=None,
    )

    application_repository.get_by_id.return_value = application

    with pytest.raises(CannotRestoreApplication):
        use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    restore_application_service.validate_rental.assert_not_called()
    application_repository.update.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


@pytest.mark.parametrize(
    "previous_status",
    [
        ApplicationStatus.PAID,
        ApplicationStatus.COMPLETED,
    ],
)
def test_paid_or_completed_previous_status_cannot_be_restored(
    previous_status,
    use_case,
    application_repository,
    restore_application_service,
    unit_of_work,
    dto,
    current_admin,
):
    application = make_application(
        status=ApplicationStatus.CANCELLED,
        previous_status=previous_status,
    )

    application_repository.get_by_id.return_value = application

    with pytest.raises(CannotRestoreApplication):
        use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    restore_application_service.validate_rental.assert_not_called()
    application_repository.update.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# RENTAL VALIDATION
# ============================================================


def test_rental_is_validated_before_restoration(
    use_case,
    application_repository,
    dto,
    current_admin,
    restore_application_service,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    restore_application_service.validate_rental.return_value = None

    use_case.execute(
        dto=dto,
        current_admin=current_admin,
    )

    restore_application_service.validate_rental.assert_called_once_with(
        application
    )