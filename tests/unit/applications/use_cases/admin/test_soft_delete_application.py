from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from modules.applications.application.dtos.application_id_dto import (
    ApplicationIdDTO,
)
from modules.applications.application.use_cases.admin.soft_delete_application import (
    SoftDeleteApplicationUseCase,
)
from modules.applications.domain.entities.application import Application
from modules.applications.domain.enums import ApplicationStatus, EventType
from modules.applications.domain.exceptions import (
    ApplicationNotFound,
    ApplicationAlreadyDeleted,
    CannotDeleteApplication,
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
    deleted_at=None,
):
    return Application(
        id=application_id,
        user_id=user_id,
        vehicle_id=vehicle_id,
        status=status,
        deleted_at=deleted_at,
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
    return SoftDeleteApplicationUseCase(
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
# ALREADY DELETED
# ============================================================

def test_already_deleted_application_cannot_be_deleted(
    use_case,
    application_repository,
    event_service,
    unit_of_work,
    dto,
    current_admin,
):
    deleted_at = datetime.now(timezone.utc)

    application = make_application(
        status=ApplicationStatus.COMPLETED,
        deleted_at=deleted_at,
    )

    application_repository.get_by_id.return_value = application

    with pytest.raises(ApplicationAlreadyDeleted):
        use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    application_repository.update.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# INVALID STATUSES
# ============================================================

@pytest.mark.parametrize(
    "status",
    [
        ApplicationStatus.DRAFT,
        ApplicationStatus.SUBMITTED,
        ApplicationStatus.APPROVED,
        ApplicationStatus.PAID,
    ],
)
def test_application_with_non_final_status_cannot_be_deleted(
    status,
    use_case,
    application_repository,
    event_service,
    unit_of_work,
    dto,
    current_admin,
):
    application = make_application(
        status=status,
    )

    application_repository.get_by_id.return_value = application

    with pytest.raises(CannotDeleteApplication):
        use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    application_repository.update.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# SUCCESSFUL SOFT DELETE
# ============================================================

@pytest.mark.parametrize(
    "status",
    [
        ApplicationStatus.CANCELLED,
        ApplicationStatus.COMPLETED,
        ApplicationStatus.REJECTED,
    ],
)
def test_final_status_application_can_be_soft_deleted(
    status,
    use_case,
    application_repository,
    event_service,
    unit_of_work,
    dto,
    current_admin,
):
    application = make_application(
        status=status,
    )

    application_repository.get_by_id.return_value = application

    result = use_case.execute(
        dto=dto,
        current_admin=current_admin,
    )

    assert result is application
    assert application.deleted_at is not None
    assert application.deleted_at.tzinfo is not None
    assert application.deleted_at.utcoffset() == timezone.utc.utcoffset(
        application.deleted_at
    )

    application_repository.update.assert_called_once_with(
        application
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# DELETED_AT IS SET
# ============================================================

def test_deleted_at_is_set_when_soft_delete_succeeds(
    use_case,
    application_repository,
    dto,
    current_admin,
):
    application = make_application(
        status=ApplicationStatus.COMPLETED,
        deleted_at=None,
    )

    application_repository.get_by_id.return_value = application

    before = datetime.now(timezone.utc)

    use_case.execute(
        dto=dto,
        current_admin=current_admin,
    )

    after = datetime.now(timezone.utc)

    assert application.deleted_at is not None
    assert before <= application.deleted_at <= after


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

def test_soft_delete_event_is_logged(
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
        type=EventType.APPLICATION_SOFT_DELETED,
        message="Dossier supprimé par administrateur.",
        event_metadata={
            "deleted_by": "admin-1",
            "vehicle_id": "vehicle-1",
            "status": ApplicationStatus.COMPLETED.value,
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

def test_returns_soft_deleted_application(
    use_case,
    application_repository,
    dto,
    current_admin,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    result = use_case.execute(
        dto=dto,
        current_admin=current_admin,
    )

    assert result is application
    assert result.deleted_at is not None