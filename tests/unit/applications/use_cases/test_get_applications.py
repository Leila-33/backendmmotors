from unittest.mock import Mock, patch

import pytest

from modules.applications.application.dtos.get_applications_dto import (
    GetApplicationsDTO,
)

from modules.applications.application.use_cases.get_applications import (
    GetApplicationsUseCase,
)
from modules.applications.domain.exceptions import CannotRestoreApplication
from modules.auth.domain.enums import UserRole
from core.pagination.paginated_result import PaginatedResult

@pytest.fixture
def application_repository():
    return Mock()


@pytest.fixture
def restore_application_service():
    return Mock()


@pytest.fixture
def use_case(
    application_repository,
    restore_application_service,
):
    return GetApplicationsUseCase(
        application_repository=application_repository,
        restore_application_service=restore_application_service,
    )


@pytest.fixture
def dto():
    dto = Mock(spec=GetApplicationsDTO)

    dto.page = 1
    dto.limit = 10
    dto.search = "BMW"
    dto.status = None
    dto.application_type = None
    dto.sort = "created_at_desc"
    dto.view_mode = "active"

    return dto


@pytest.fixture
def application():
    application = Mock()

    application.id = "application-1"
    application.user_id = "user-1"
    application.vehicle_id = "vehicle-1"

    return application


def test_client_searches_by_vehicle(
    use_case,
    application_repository,
    restore_application_service,
    dto,
    application,
):
    application_repository.find_all.return_value = (
        [application],
        1,
    )

    result = use_case.execute(
        dto=dto,
        role=UserRole.CLIENT,
        user_id="user-1",
    )

    application_repository.find_all.assert_called_once_with(
        page=1,
        limit=10,
        search="BMW",
        search_field="vehicle",
        status=None,
        application_type=None,
        sort="created_at_desc",
        view_mode="active",
        user_id="user-1",
        role=UserRole.CLIENT,
    )

    assert result.total == 1


def test_admin_searches_by_user(
    use_case,
    application_repository,
    dto,
    application,
):
    application_repository.find_all.return_value = (
        [application],
        1,
    )

    result = use_case.execute(
        dto=dto,
        role=UserRole.ADMIN,
        user_id="admin-1",
    )

    application_repository.find_all.assert_called_once_with(
        page=1,
        limit=10,
        search="BMW",
        search_field="user",
        status=None,
        application_type=None,
        sort="created_at_desc",
        view_mode="active",
        user_id="admin-1",
        role=UserRole.ADMIN,
    )

    assert result.total == 1


def test_returns_empty_result_when_no_application_found(
    use_case,
    application_repository,
    restore_application_service,
    dto,
):
    application_repository.find_all.return_value = (
        [],
        0,
    )

    result = use_case.execute(
        dto=dto,
        role=UserRole.CLIENT,
        user_id="user-1",
    )

    assert isinstance(result, PaginatedResult)
    assert result.items == []
    assert result.total == 0
    assert result.page == 1
    assert result.limit == 10
    assert result.total_pages == 0


def test_calculates_pages_correctly(
    use_case,
    application_repository,
    dto,
    application,
):
    application_repository.find_all.return_value = (
        [application],
        25,
    )

    result = use_case.execute(
        dto=dto,
        role=UserRole.CLIENT,
        user_id="user-1",
    )

    assert result.total_pages == 3


def test_calculates_one_page_when_total_is_less_than_limit(
    use_case,
    application_repository,
    dto,
    application,
):
    application_repository.find_all.return_value = (
        [application],
        7,
    )

    result = use_case.execute(
        dto=dto,
        role=UserRole.CLIENT,
        user_id="user-1",
    )

    assert result.total_pages == 1


def test_calculates_exact_number_of_pages_when_total_is_multiple_of_limit(
    use_case,
    application_repository,
    dto,
    application,
):
    application_repository.find_all.return_value = (
        [application],
        20,
    )

    result = use_case.execute(
        dto=dto,
        role=UserRole.CLIENT,
        user_id="user-1",
    )

    assert result.total_pages == 2


def test_client_has_cancel_permission_based_on_policy(
    use_case,
    application_repository,
    dto,
    application,
):
    application_repository.find_all.return_value = (
        [application],
        1,
    )

    with patch(
        "modules.applications.application.use_cases.get_applications."
        "CancelApplicationPolicy.can_cancel",
        return_value=True,
    ) as mock_can_cancel:
        result = use_case.execute(
            dto=dto,
            role=UserRole.CLIENT,
            user_id="user-1",
        )

    mock_can_cancel.assert_called_once_with(application)

    assert len(result.items) == 1
    assert result.items[0].can_cancel is True


def test_client_cannot_restore_archive_or_delete(
    use_case,
    application_repository,
    restore_application_service,
    dto,
    application,
):
    application_repository.find_all.return_value = (
        [application],
        1,
    )

    result = use_case.execute(
        dto=dto,
        role=UserRole.CLIENT,
        user_id="user-1",
    )

    item = result.items[0]

    assert item.can_restore_cancelled is False
    assert item.can_archive is False
    assert item.can_delete is False

    restore_application_service.validate_rental.assert_not_called()


def test_admin_can_restore_application_when_all_validations_pass(
    use_case,
    application_repository,
    restore_application_service,
    dto,
    application,
):
    application_repository.find_all.return_value = (
        [application],
        1,
    )

    with patch(
        "modules.applications.application.use_cases.get_applications."
        "RestoreApplicationPolicy.validate"
    ) as mock_validate:

        result = use_case.execute(
            dto=dto,
            role=UserRole.ADMIN,
            user_id="admin-1",
        )

    mock_validate.assert_called_once_with(application)
    restore_application_service.validate_rental.assert_called_once_with(
        application
    )

    item = result.items[0]

    assert item.can_restore_cancelled is True


def test_admin_cannot_restore_when_policy_rejects_application(
    use_case,
    application_repository,
    restore_application_service,
    dto,
    application,
):
    application_repository.find_all.return_value = (
        [application],
        1,
    )

    with patch(
        "modules.applications.application.use_cases.get_applications."
        "RestoreApplicationPolicy.validate",
        side_effect=CannotRestoreApplication(),
    ) as mock_validate:

        result = use_case.execute(
            dto=dto,
            role=UserRole.ADMIN,
            user_id="admin-1",
        )

    mock_validate.assert_called_once_with(application)

    restore_application_service.validate_rental.assert_not_called()

    item = result.items[0]

    assert item.can_restore_cancelled is False


def test_admin_cannot_restore_when_rental_validation_fails(
    use_case,
    application_repository,
    restore_application_service,
    dto,
    application,
):
    application_repository.find_all.return_value = (
        [application],
        1,
    )

    restore_application_service.validate_rental.side_effect = (
        CannotRestoreApplication()
    )

    with patch(
        "modules.applications.application.use_cases.get_applications."
        "RestoreApplicationPolicy.validate"
    ) as mock_validate:

        result = use_case.execute(
            dto=dto,
            role=UserRole.ADMIN,
            user_id="admin-1",
        )

    mock_validate.assert_called_once_with(application)

    restore_application_service.validate_rental.assert_called_once_with(
        application
    )

    item = result.items[0]

    assert item.can_restore_cancelled is False


def test_admin_can_archive_based_on_policy(
    use_case,
    application_repository,
    dto,
    application,
):
    application_repository.find_all.return_value = (
        [application],
        1,
    )

    with patch(
        "modules.applications.application.use_cases.get_applications."
        "ArchiveApplicationPolicy.can_archive",
        return_value=True,
    ) as mock_can_archive:

        result = use_case.execute(
            dto=dto,
            role=UserRole.ADMIN,
            user_id="admin-1",
        )

    mock_can_archive.assert_called_once_with(application)

    item = result.items[0]

    assert item.can_archive is True


def test_admin_can_delete_based_on_policy(
    use_case,
    application_repository,
    dto,
    application,
):
    application_repository.find_all.return_value = (
        [application],
        1,
    )

    with patch(
        "modules.applications.application.use_cases.get_applications."
        "SoftDeleteApplicationPolicy.can_delete",
        return_value=True,
    ) as mock_can_delete:

        result = use_case.execute(
            dto=dto,
            role=UserRole.ADMIN,
            user_id="admin-1",
        )

    mock_can_delete.assert_called_once_with(application)

    item = result.items[0]

    assert item.can_delete is True


def test_admin_returns_all_permissions_according_to_policies(
    use_case,
    application_repository,
    restore_application_service,
    dto,
    application,
):
    application_repository.find_all.return_value = (
        [application],
        1,
    )

    with (
        patch(
            "modules.applications.application.use_cases.get_applications."
            "CancelApplicationPolicy.can_cancel",
            return_value=True,
        ),
        patch(
            "modules.applications.application.use_cases.get_applications."
            "RestoreApplicationPolicy.validate",
        ),
        patch(
            "modules.applications.application.use_cases.get_applications."
            "ArchiveApplicationPolicy.can_archive",
            return_value=True,
        ),
        patch(
            "modules.applications.application.use_cases.get_applications."
            "SoftDeleteApplicationPolicy.can_delete",
            return_value=True,
        ),
    ):
        result = use_case.execute(
            dto=dto,
            role=UserRole.ADMIN,
            user_id="admin-1",
        )

    item = result.items[0]

    assert item.can_cancel is True
    assert item.can_restore_cancelled is True
    assert item.can_archive is True
    assert item.can_delete is True


def test_builds_one_item_per_application(
    use_case,
    application_repository,
    dto,
):
    application_1 = Mock()
    application_1.id = "application-1"
    application_1.user_id = "user-1"
    application_1.vehicle_id = "vehicle-1"

    application_2 = Mock()
    application_2.id = "application-2"
    application_2.user_id = "user-2"
    application_2.vehicle_id = "vehicle-2"

    application_repository.find_all.return_value = (
        [application_1, application_2],
        2,
    )

    result = use_case.execute(
        dto=dto,
        role=UserRole.CLIENT,
        user_id="user-1",
    )

    assert len(result.items) == 2
    assert result.items[0].application is application_1
    assert result.items[1].application is application_2


def test_returns_pagination_information(
    use_case,
    application_repository,
    dto,
    application,
):
    dto.page = 2
    dto.limit = 5

    application_repository.find_all.return_value = (
        [application],
        11,
    )

    result = use_case.execute(
        dto=dto,
        role=UserRole.CLIENT,
        user_id="user-1",
    )

    assert result.page == 2
    assert result.limit == 5
    assert result.total == 11
    assert result.total_pages == 3