from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from modules.applications.application.dtos.application_id_dto import (
    ApplicationIdDTO,
)
from modules.applications.application.results.get_application_result import (
    GetApplicationResult,
)
from modules.applications.application.use_cases.get_application import (
    GetApplicationUseCase,
)
from modules.applications.domain.entities.application import (
    Application,
)
from modules.applications.domain.enums import ApplicationStatus
from modules.applications.domain.exceptions import (
    ApplicationNotFound,
)
from modules.auth.domain.enums import UserRole


# ============================================================
# HELPERS
# ============================================================


def make_application(
    *,
    application_id="application-1",
    user_id="user-1",
    vehicle_id="vehicle-1",
    status=None,
):
    if status is None:
        status = ApplicationStatus.DRAFT

    return Application(
        id=application_id,
        user_id=user_id,
        vehicle_id=vehicle_id,
        status=status,
    )


def make_current_user(
    *,
    user_id="user-1",
    role=None,
):
    if role is None:
        role = UserRole.CLIENT

    return SimpleNamespace(
        id=user_id,
        role=role,
    )


def make_payment(
    *,
    status,
):
    return SimpleNamespace(
        status=status,
    )


def make_dto(
    *,
    application_id="application-1",
):
    return ApplicationIdDTO(
        application_id=application_id,
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def application_repository():
    return Mock()


@pytest.fixture
def payment_repository():
    return Mock()


@pytest.fixture
def use_case(
    application_repository,
    payment_repository,
):
    return GetApplicationUseCase(
        application_repository=application_repository,
        payment_repository=payment_repository,
    )


@pytest.fixture
def application():
    return make_application()


@pytest.fixture
def current_user():
    return make_current_user()


@pytest.fixture
def dto():
    return make_dto()


# ============================================================
# APPLICATION NOT FOUND
# ============================================================


def test_application_not_found(
    use_case,
    application_repository,
    payment_repository,
    dto,
    current_user,
):
    application_repository.get_full_by_id.return_value = None

    with pytest.raises(
        ApplicationNotFound
    ):
        use_case.execute(
            dto=dto,
            current_user=current_user,
        )

    application_repository.get_full_by_id.assert_called_once_with(
        "application-1"
    )

    payment_repository.get_latest_by_application_id.assert_not_called()


# ============================================================
# AUTHORIZATION
# ============================================================


def test_user_can_access_own_application(
    use_case,
    application_repository,
    payment_repository,
    application,
    dto,
    current_user,
):
    application_repository.get_full_by_id.return_value = application
    payment_repository.get_latest_by_application_id.return_value = None

    result = use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    assert isinstance(
        result,
        GetApplicationResult,
    )

    assert result.application is application
    assert result.payment_status is None


def test_user_cannot_access_another_users_application(
    use_case,
    application_repository,
    payment_repository,
    application,
    dto,
):
    current_user = make_current_user(
        user_id="another-user",
    )

    application_repository.get_full_by_id.return_value = application

    with pytest.raises(
        ApplicationNotFound
    ):
        use_case.execute(
            dto=dto,
            current_user=current_user,
        )

    payment_repository.get_latest_by_application_id.assert_not_called()


def test_admin_can_access_another_users_application(
    use_case,
    application_repository,
    payment_repository,
    application,
    dto,
):
    admin = make_current_user(
        user_id="admin-1",
        role=UserRole.ADMIN,
    )

    application_repository.get_full_by_id.return_value = application
    payment_repository.get_latest_by_application_id.return_value = None

    result = use_case.execute(
        dto=dto,
        current_user=admin,
    )

    assert isinstance(
        result,
        GetApplicationResult,
    )

    assert result.application is application
    assert result.payment_status is None


# ============================================================
# PAYMENT
# ============================================================


def test_payment_is_loaded(
    use_case,
    application_repository,
    payment_repository,
    application,
    dto,
    current_user,
):
    application_repository.get_full_by_id.return_value = application
    payment_repository.get_latest_by_application_id.return_value = None

    use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    payment_repository.get_latest_by_application_id.assert_called_once_with(
        "application-1"
    )


def test_payment_status_is_returned(
    use_case,
    application_repository,
    payment_repository,
    application,
    dto,
    current_user,
):
    application_repository.get_full_by_id.return_value = application

    payment_status = next(
        iter(
            [
                status
                for status in getattr(
                    application.status.__class__,
                    "__members__",
                    {},
                )
            ]
        ),
        None,
    )

    # On utilise un objet simple afin de ne pas dépendre
    # des membres exacts de l'enum PaymentStatus.
    payment = SimpleNamespace(
        status=SimpleNamespace(
            value="PAID",
        )
    )

    payment_repository.get_latest_by_application_id.return_value = (
        payment
    )

    result = use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    assert result.payment_status == "PAID"

    payment_repository.get_latest_by_application_id.assert_called_once_with(
        "application-1"
    )


def test_payment_status_is_none_when_no_payment_exists(
    use_case,
    application_repository,
    payment_repository,
    application,
    dto,
    current_user,
):
    application_repository.get_full_by_id.return_value = application
    payment_repository.get_latest_by_application_id.return_value = None

    result = use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    assert result.payment_status is None


# ============================================================
# RESULT
# ============================================================


def test_result_contains_application(
    use_case,
    application_repository,
    payment_repository,
    application,
    dto,
    current_user,
):
    application_repository.get_full_by_id.return_value = application
    payment_repository.get_latest_by_application_id.return_value = None

    result = use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    assert isinstance(
        result,
        GetApplicationResult,
    )

    assert result.application is application


def test_result_contains_payment_status(
    use_case,
    application_repository,
    payment_repository,
    application,
    dto,
    current_user,
):
    application_repository.get_full_by_id.return_value = application

    payment = SimpleNamespace(
        status=SimpleNamespace(
            value="COMPLETED",
        )
    )

    payment_repository.get_latest_by_application_id.return_value = (
        payment
    )

    result = use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    assert result.payment_status == "COMPLETED"


# ============================================================
# REPOSITORY ARGUMENTS
# ============================================================


def test_application_repository_receives_application_id(
    use_case,
    application_repository,
    payment_repository,
    dto,
    current_user,
):
    application = make_application(
        application_id="application-42",
        user_id="user-1",
    )

    dto = make_dto(
        application_id="application-42",
    )

    application_repository.get_full_by_id.return_value = application
    payment_repository.get_latest_by_application_id.return_value = None

    use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    application_repository.get_full_by_id.assert_called_once_with(
        "application-42"
    )


def test_payment_repository_receives_loaded_application_id(
    use_case,
    application_repository,
    payment_repository,
    dto,
    current_user,
):
    application = make_application(
        application_id="application-42",
        user_id="user-1",
    )

    application_repository.get_full_by_id.return_value = application
    payment_repository.get_latest_by_application_id.return_value = None

    use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    payment_repository.get_latest_by_application_id.assert_called_once_with(
        "application-42"
    )


# ============================================================
# COMPLETE FLOW
# ============================================================


def test_get_application_complete_flow(
    use_case,
    application_repository,
    payment_repository,
):
    application = make_application(
        application_id="application-42",
        user_id="user-42",
        vehicle_id="vehicle-42",
        status=ApplicationStatus.DRAFT,
    )

    current_user = make_current_user(
        user_id="user-42",
        role=UserRole.CLIENT,
    )

    dto = make_dto(
        application_id="application-42",
    )

    payment = SimpleNamespace(
        status=SimpleNamespace(
            value="PAID",
        )
    )

    application_repository.get_full_by_id.return_value = application
    payment_repository.get_latest_by_application_id.return_value = payment

    result = use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    assert isinstance(
        result,
        GetApplicationResult,
    )

    assert result.application is application
    assert result.payment_status == "PAID"

    application_repository.get_full_by_id.assert_called_once_with(
        "application-42"
    )

    payment_repository.get_latest_by_application_id.assert_called_once_with(
        "application-42"
    )