from unittest.mock import Mock

import pytest

from modules.applications.application.dtos.application_id_dto import (
    ApplicationIdDTO,
)
from modules.applications.application.use_cases.get_application import (
    GetApplicationUseCase,
)
from modules.applications.domain.entities.application import Application
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.auth.domain.enums import UserRole


@pytest.fixture
def application_repository():
    return Mock()



@pytest.fixture
def use_case(application_repository):
    return GetApplicationUseCase(
        application_repository=application_repository,
    )


@pytest.fixture
def dto():
    return ApplicationIdDTO(application_id="application-1")


@pytest.fixture
def application():
    application = Mock(spec=Application)
    application.id = "application-1"
    application.user_id = "user-1"
    return application


@pytest.fixture
def regular_user():
    user = Mock()
    user.id = "user-1"
    user.role = UserRole.CLIENT
    return user


@pytest.fixture
def admin_user():
    user = Mock()
    user.id = "admin-1"
    user.role = UserRole.ADMIN
    return user


def test_returns_application(
    use_case,
    application_repository,
    dto,
    application,
    regular_user,
):

    application_repository.get_full_by_id.return_value = application

    result = use_case.execute(
        dto=dto,
        current_user=regular_user,
    )

    assert result == (application)

    application_repository.get_full_by_id.assert_called_once_with(
        "application-1"
    )



def test_raises_application_not_found_when_application_does_not_exist(
    use_case,
    application_repository,
    dto,
    regular_user,
):
    application_repository.get_full_by_id.return_value = None

    with pytest.raises(ApplicationNotFound):
        use_case.execute(
            dto=dto,
            current_user=regular_user,
        )

    application_repository.get_full_by_id.assert_called_once_with(
        "application-1"
    )



def test_raises_application_not_found_when_user_is_not_owner(
    use_case,
    application_repository,
    dto,
    application,
):
    current_user = Mock()
    current_user.id = "user-2"
    current_user.role = UserRole.CLIENT

    application_repository.get_full_by_id.return_value = application

    with pytest.raises(ApplicationNotFound):
        use_case.execute(
            dto=dto,
            current_user=current_user,
        )

    application_repository.get_full_by_id.assert_called_once_with(
        "application-1"
    )



def test_admin_can_access_application_of_another_user(
    use_case,
    application_repository,
    dto,
    application,
    admin_user,
):

    application_repository.get_full_by_id.return_value = application

    result = use_case.execute(
        dto=dto,
        current_user=admin_user,
    )

    assert result == (application)

    application_repository.get_full_by_id.assert_called_once_with(
        "application-1"
    )



def test_owner_can_access_own_application(
    use_case,
    application_repository,
    dto,
    application,
    regular_user,
):

    application_repository.get_full_by_id.return_value = application

    result = use_case.execute(
        dto=dto,
        current_user=regular_user,
    )

    assert result is application


def test_returns_application(
    use_case,
    application_repository,
    dto,
    application,
    regular_user,
):
    application_repository.get_full_by_id.return_value = application

    result = use_case.execute(
        dto=dto,
        current_user=regular_user,
    )

    assert result == (application, None)
