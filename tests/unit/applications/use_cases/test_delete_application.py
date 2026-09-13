from unittest.mock import Mock

import pytest

from modules.applications.application.dtos.application_id_dto import (
    ApplicationIdDTO,
)
from modules.applications.application.results.delete_application_result import (
    DeleteApplicationResult,
)
from modules.applications.application.use_cases.delete_application import (
    DeleteApplicationUseCase,
)
from modules.applications.domain.entities.application import Application
from modules.applications.domain.enums import ApplicationStatus
from modules.applications.domain.exceptions import (
    ApplicationCannotBeDeleted,
    ApplicationNotFound,
)
from modules.auth.domain.entities.user import User
from modules.auth.domain.enums import UserRole
from modules.auth.domain.exceptions import Forbidden
from modules.notifications.domain.enums import NotificationEntityType


# ============================================================
# HELPERS
# ============================================================


def make_application(
    *,
    application_id: str = "application-1",
    user_id: str = "user-1",
    status: ApplicationStatus = ApplicationStatus.DRAFT,
):
    return Application(
        id=application_id,
        user_id=user_id,
        vehicle_id="vehicle-1",
        status=status,
    )


def make_current_user(
    *,
    user_id: str = "user-1",
):
    return User(
        id=user_id,
        first_name="Leila",
        last_name="El",
        email="Leila@example.com",
        password="password",
        role=UserRole.CLIENT,
        is_active=True,
        is_verified=True,
        accepted_cgu=True,
    )


def make_document(
    s3_key: str | None = "documents/application-1/file.pdf",
):
    return Mock(
        s3_key=s3_key
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def application_repo():
    return Mock()


@pytest.fixture
def document_repo():
    repo = Mock()
    repo.get_by_application.return_value = []
    return repo


@pytest.fixture
def trade_in_repo():
    repo = Mock()
    repo.get_by_application.return_value = None
    return repo


@pytest.fixture
def financing_repo():
    repo = Mock()
    repo.get_by_application.return_value = None
    return repo


@pytest.fixture
def application_option_repo():
    repo = Mock()
    repo.get_by_application.return_value = []
    return repo


@pytest.fixture
def reservation_repo():
    repo = Mock()
    repo.get_by_application.return_value = None
    return repo


@pytest.fixture
def event_repo():
    repo = Mock()
    repo.get_by_application.return_value = []
    return repo


@pytest.fixture
def notification_repo():
    repo = Mock()
    repo.get_by_application.return_value = []
    return repo


@pytest.fixture
def s3_service():
    return Mock()


@pytest.fixture
def uow():
    return Mock()

@pytest.fixture
def use_case(
    application_repo,
    document_repo,
    trade_in_repo,
    financing_repo,
    application_option_repo,
    reservation_repo,
    event_repo,
    notification_repo,
    s3_service,
    uow,
):
    return DeleteApplicationUseCase(
        application_repo=application_repo,
        document_repo=document_repo,
        trade_in_repo=trade_in_repo,
        financing_repo=financing_repo,
        application_option_repo=application_option_repo,
        reservation_repo=reservation_repo,
        event_repo=event_repo,
        notification_repo=notification_repo,
        s3_service=s3_service,
        uow=uow,
    )


@pytest.fixture
def dto():
    return ApplicationIdDTO(
        application_id="application-1"
    )


@pytest.fixture
def current_user():
    return make_current_user()


# ============================================================
# APPLICATION NOT FOUND
# ============================================================


def test_application_not_found(
    use_case,
    application_repo,
    uow,
    dto,
    current_user,
):
    application_repo.get_by_id.return_value = None

    with pytest.raises(ApplicationNotFound):
        use_case.execute(
            dto=dto,
            current_user=current_user,
        )

    application_repo.get_by_id.assert_called_once_with(
        "application-1"
    )

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()


# ============================================================
# SECURITY
# ============================================================


def test_user_cannot_delete_another_users_application(
    use_case,
    application_repo,
    uow,
    dto,
):
    application = make_application(
        user_id="owner-1"
    )

    current_user = make_current_user(
        user_id="another-user"
    )

    application_repo.get_by_id.return_value = application

    with pytest.raises(Forbidden):
        use_case.execute(
            dto=dto,
            current_user=current_user,
        )

    application_repo.delete.assert_not_called()
    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_owner_can_delete_application(
    use_case,
    application_repo,
    uow,
    dto,
):
    application = make_application(
        user_id="user-1"
    )

    current_user = make_current_user(
        user_id="user-1"
    )

    application_repo.get_by_id.return_value = application

    result = use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    assert result.application_id == "application-1"

    application_repo.delete.assert_called_once_with(
        "application-1"
    )

    uow.commit.assert_called_once()


# ============================================================
# BUSINESS RULE — ONLY DRAFT
# ============================================================


@pytest.mark.parametrize(
    "status",
    [
        ApplicationStatus.PAID,
        ApplicationStatus.COMPLETED,
        ApplicationStatus.CANCELLED,
    ],
)
def test_non_draft_application_cannot_be_deleted(
    status,
    use_case,
    application_repo,
    uow,
    dto,
    current_user,
):
    application = make_application(
        status=status
    )

    application_repo.get_by_id.return_value = application

    with pytest.raises(ApplicationCannotBeDeleted):
        use_case.execute(
            dto=dto,
            current_user=current_user,
        )

    application_repo.delete.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_draft_application_can_be_deleted(
    use_case,
    application_repo,
    uow,
    dto,
    current_user,
):
    application = make_application(
        status=ApplicationStatus.DRAFT
    )

    application_repo.get_by_id.return_value = application

    result = use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    assert isinstance(
        result,
        DeleteApplicationResult,
    )

    assert result.application_id == "application-1"

    application_repo.delete.assert_called_once_with(
        "application-1"
    )

    uow.commit.assert_called_once()


# ============================================================
# DOCUMENTS / S3
# ============================================================


def test_documents_are_loaded_before_deletion(
    use_case,
    application_repo,
    document_repo,
    dto,
    current_user,
):
    application = make_application()

    application_repo.get_by_id.return_value = application
    document_repo.get_by_application.return_value = []

    use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    document_repo.get_by_application.assert_called_once_with(
        "application-1"
    )


def test_s3_files_are_deleted(
    use_case,
    application_repo,
    document_repo,
    s3_service,
    dto,
    current_user,
):
    application = make_application()

    documents = [
        make_document("documents/application-1/id.pdf"),
        make_document("documents/application-1/payroll.pdf"),
        make_document("documents/application-1/rib.pdf"),
    ]

    application_repo.get_by_id.return_value = application
    document_repo.get_by_application.return_value = documents

    use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    assert s3_service.delete_file.call_count == 3

    s3_service.delete_file.assert_any_call(
        "documents/application-1/id.pdf"
    )

    s3_service.delete_file.assert_any_call(
        "documents/application-1/payroll.pdf"
    )

    s3_service.delete_file.assert_any_call(
        "documents/application-1/rib.pdf"
    )


def test_document_without_s3_key_is_not_deleted_from_s3(
    use_case,
    application_repo,
    document_repo,
    s3_service,
    dto,
    current_user,
):
    application = make_application()

    documents = [
        make_document(None),
        make_document("documents/application-1/file.pdf"),
    ]

    application_repo.get_by_id.return_value = application
    document_repo.get_by_application.return_value = documents

    use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    s3_service.delete_file.assert_called_once_with(
        "documents/application-1/file.pdf"
    )


def test_no_s3_file_is_deleted_when_documents_have_no_keys(
    use_case,
    application_repo,
    document_repo,
    s3_service,
    dto,
    current_user,
):
    application = make_application()

    documents = [
        make_document(None),
        make_document(None),
    ]

    application_repo.get_by_id.return_value = application
    document_repo.get_by_application.return_value = documents

    use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    s3_service.delete_file.assert_not_called()


# ============================================================
# CHILD ENTITIES
# ============================================================


def test_documents_are_deleted(
    use_case,
    application_repo,
    document_repo,
    dto,
    current_user,
):
    application_repo.get_by_id.return_value = make_application()
    document_repo.get_by_application.return_value = []

    use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    document_repo.delete_by_application.assert_called_once_with(
        "application-1"
    )


def test_events_are_deleted(
    use_case,
    application_repo,
    event_repo,
    dto,
    current_user,
):
    application_repo.get_by_id.return_value = make_application()

    use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    event_repo.delete_by_application.assert_called_once_with(
        "application-1"
    )


def test_notifications_are_deleted(
    use_case,
    application_repo,
    notification_repo,
    dto,
    current_user,
):
    application_repo.get_by_id.return_value = make_application()

    use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    notification_repo.delete_by_entity.assert_called_once_with(
        NotificationEntityType.APPLICATION,
        "application-1",
    )


def test_trade_in_is_deleted(
    use_case,
    application_repo,
    trade_in_repo,
    dto,
    current_user,
):
    application_repo.get_by_id.return_value = make_application()

    use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    trade_in_repo.delete_by_application.assert_called_once_with(
        "application-1"
    )


def test_financing_is_deleted(
    use_case,
    application_repo,
    financing_repo,
    dto,
    current_user,
):
    application_repo.get_by_id.return_value = make_application()

    use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    financing_repo.delete_by_application.assert_called_once_with(
        "application-1"
    )


def test_application_options_are_deleted(
    use_case,
    application_repo,
    application_option_repo,
    dto,
    current_user,
):
    application_repo.get_by_id.return_value = make_application()

    use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    application_option_repo.delete_by_application.assert_called_once_with(
        "application-1"
    )


def test_reservation_is_deleted(
    use_case,
    application_repo,
    reservation_repo,
    dto,
    current_user,
):
    application_repo.get_by_id.return_value = make_application()

    use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    reservation_repo.delete_by_application.assert_called_once_with(
        "application-1"
    )


# ============================================================
# APPLICATION
# ============================================================


def test_application_is_deleted(
    use_case,
    application_repo,
    dto,
    current_user,
):
    application_repo.get_by_id.return_value = make_application()

    use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    application_repo.delete.assert_called_once_with(
        "application-1"
    )


# ============================================================
# COMMIT / RESULT
# ============================================================


def test_commit_is_called(
    use_case,
    application_repo,
    uow,
    dto,
    current_user,
):
    application_repo.get_by_id.return_value = make_application()

    use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()


def test_delete_application_result_is_returned(
    use_case,
    application_repo,
    dto,
    current_user,
):
    application_repo.get_by_id.return_value = make_application()

    result = use_case.execute(
        dto=dto,
        current_user=current_user,
    )

    assert isinstance(
        result,
        DeleteApplicationResult,
    )

    assert result.application_id == "application-1"


# ============================================================
# ROLLBACK / ERRORS
# ============================================================


def test_document_loading_error_rolls_back(
    use_case,
    application_repo,
    document_repo,
    uow,
    dto,
    current_user,
):
    application_repo.get_by_id.return_value = make_application()

    document_repo.get_by_application.side_effect = RuntimeError(
        "document repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="document repository error",
    ):
        use_case.execute(
            dto=dto,
            current_user=current_user,
        )

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()


def test_s3_deletion_error_rolls_back(
    use_case,
    application_repo,
    document_repo,
    s3_service,
    uow,
    dto,
    current_user,
):
    application_repo.get_by_id.return_value = make_application()

    document_repo.get_by_application.return_value = [
        make_document("documents/application-1/file.pdf")
    ]

    s3_service.delete_file.side_effect = RuntimeError(
        "s3 error"
    )

    with pytest.raises(
        RuntimeError,
        match="s3 error",
    ):
        use_case.execute(
            dto=dto,
            current_user=current_user,
        )

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()


def test_child_delete_error_rolls_back(
    use_case,
    application_repo,
    document_repo,
    event_repo,
    uow,
    dto,
    current_user,
):
    application_repo.get_by_id.return_value = make_application()
    document_repo.get_by_application.return_value = []

    event_repo.delete_by_application.side_effect = RuntimeError(
        "event deletion error"
    )

    with pytest.raises(
        RuntimeError,
        match="event deletion error",
    ):
        use_case.execute(
            dto=dto,
            current_user=current_user,
        )

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()


def test_application_delete_error_rolls_back(
    use_case,
    application_repo,
    uow,
    dto,
    current_user,
):
    application_repo.get_by_id.return_value = make_application()

    application_repo.delete.side_effect = RuntimeError(
        "application deletion error"
    )

    with pytest.raises(
        RuntimeError,
        match="application deletion error",
    ):
        use_case.execute(
            dto=dto,
            current_user=current_user,
        )

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()


def test_commit_error_rolls_back(
    use_case,
    application_repo,
    uow,
    dto,
    current_user,
):
    application_repo.get_by_id.return_value = make_application()

    uow.commit.side_effect = RuntimeError(
        "commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="commit error",
    ):
        use_case.execute(
            dto=dto,
            current_user=current_user,
        )

    uow.commit.assert_called_once()
    uow.rollback.assert_called_once()

