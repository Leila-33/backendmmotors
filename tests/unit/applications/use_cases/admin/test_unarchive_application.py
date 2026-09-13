from unittest.mock import Mock

import pytest

from modules.applications.application.dtos.application_id_dto import (
    ApplicationIdDTO,
)
from modules.applications.application.use_cases.admin.unarchive_application import (
    UnarchiveApplicationUseCase,
)
from modules.applications.domain.entities.application import Application
from modules.applications.domain.enums import ApplicationStatus, EventType
from modules.applications.domain.exceptions import (
    ApplicationNotArchived,
    ApplicationNotFound,
)
from modules.auth.domain.enums import UserRole


def make_current_admin(*, user_id="admin-1"):
    return Mock(
        id=user_id,
        role=UserRole.ADMIN,
    )


def make_application(
    *,
    application_id="application-1",
    user_id="user-1",
    vehicle_id="vehicle-1",
    status=ApplicationStatus.COMPLETED,
    is_archived=True,
):
    return Application(
        id=application_id,
        user_id=user_id,
        vehicle_id=vehicle_id,
        status=status,
        is_archived=is_archived,
    )


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
    application_repository,
    event_service,
    unit_of_work,
):
    return UnarchiveApplicationUseCase(
        application_repository=application_repository,
        event_service=event_service,
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
    event_service,
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
        "application-1"
    )

    application_repository.update.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# APPLICATION NOT ARCHIVED
# ============================================================

def test_non_archived_application_cannot_be_unarchived(
    use_case,
    application_repository,
    event_service,
    unit_of_work,
    dto,
    current_admin,
):
    application = make_application(
        is_archived=False,
    )

    application_repository.get_by_id.return_value = application

    with pytest.raises(ApplicationNotArchived):
        use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    assert application.is_archived is False

    application_repository.update.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# SUCCESSFUL UNARCHIVE
# ============================================================

def test_archived_application_can_be_unarchived(
    use_case,
    application_repository,
    event_service,
    unit_of_work,
    dto,
    current_admin,
):
    application = make_application(
        is_archived=True,
    )

    application_repository.get_by_id.return_value = application

    result = use_case.execute(
        dto=dto,
        current_admin=current_admin,
    )

    assert result is application
    assert application.is_archived is False

    application_repository.update.assert_called_once_with(
        application
    )

    event_service.log.assert_called_once()

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# APPLICATION UPDATE
# ============================================================

def test_application_is_updated(
    use_case,
    application_repository,
    dto,
    current_admin,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    use_case.execute(
        dto=dto,
        current_admin=current_admin,
    )

    application_repository.update.assert_called_once_with(
        application
    )


# ============================================================
# EVENT
# ============================================================

def test_unarchive_event_is_logged(
    use_case,
    application_repository,
    event_service,
    dto,
    current_admin,
):
    application = make_application(
        application_id="application-1",
        user_id="user-1",
        vehicle_id="vehicle-1",
        status=ApplicationStatus.COMPLETED,
    )

    application_repository.get_by_id.return_value = application

    use_case.execute(
        dto=dto,
        current_admin=current_admin,
    )

    event_service.log.assert_called_once_with(
        application_id="application-1",
        user_id="admin-1",
        vehicle_id="vehicle-1",
        type=EventType.APPLICATION_UNARCHIVED,
        message="Dossier restauré depuis les archives.",
        event_metadata={
            "restored_by": "admin-1",
            "vehicle_id": "vehicle-1",
            "status": ApplicationStatus.COMPLETED.value,
        },
    )


# ============================================================
# EVENT WITH NONE STATUS
# ============================================================

def test_unarchive_event_contains_none_status_when_status_is_none(
    use_case,
    application_repository,
    event_service,
    dto,
    current_admin,
):
    application = make_application(
        status=None,
    )

    application_repository.get_by_id.return_value = application

    use_case.execute(
        dto=dto,
        current_admin=current_admin,
    )

    event_service.log.assert_called_once_with(
        application_id="application-1",
        user_id="admin-1",
        vehicle_id="vehicle-1",
        type=EventType.APPLICATION_UNARCHIVED,
        message="Dossier restauré depuis les archives.",
        event_metadata={
            "restored_by": "admin-1",
            "vehicle_id": "vehicle-1",
            "status": None,
        },
    )


# ============================================================
# UPDATE ERROR
# ============================================================

def test_application_update_error_rolls_back(
    use_case,
    application_repository,
    event_service,
    unit_of_work,
    dto,
    current_admin,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    application_repository.update.side_effect = RuntimeError(
        "update error"
    )

    with pytest.raises(
        RuntimeError,
        match="update error",
    ):
        use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()

    event_service.log.assert_not_called()


# ============================================================
# EVENT ERROR
# ============================================================

def test_event_error_rolls_back(
    use_case,
    application_repository,
    event_service,
    unit_of_work,
    dto,
    current_admin,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    event_service.log.side_effect = RuntimeError(
        "event error"
    )

    with pytest.raises(
        RuntimeError,
        match="event error",
    ):
        use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# COMMIT
# ============================================================

def test_commit_is_called(
    use_case,
    application_repository,
    unit_of_work,
    dto,
    current_admin,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    use_case.execute(
        dto=dto,
        current_admin=current_admin,
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# COMMIT ERROR
# ============================================================

def test_commit_error_rolls_back(
    use_case,
    application_repository,
    unit_of_work,
    dto,
    current_admin,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    unit_of_work.commit.side_effect = RuntimeError(
        "commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="commit error",
    ):
        use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# RETURNED APPLICATION
# ============================================================

def test_returns_unarchived_application(
    use_case,
    application_repository,
    dto,
    current_admin,
):
    application = make_application(
        is_archived=True,
    )

    application_repository.get_by_id.return_value = application

    result = use_case.execute(
        dto=dto,
        current_admin=current_admin,
    )

    assert result is application
    assert result.is_archived is False