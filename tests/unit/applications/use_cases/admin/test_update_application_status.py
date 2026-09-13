from unittest.mock import AsyncMock, Mock, patch

import pytest

from modules.applications.application.dtos.admin.update_application_status_dto import (
    UpdateApplicationStatusDTO,
)
from modules.applications.application.results.admin.update_application_status_result import (
    UpdateApplicationStatusResult,
)
from modules.applications.application.use_cases.admin.update_application_status import (
    UpdateApplicationStatusUseCase,
)
from modules.applications.domain.entities.application import Application
from modules.applications.domain.enums import (
    ApplicationStatus,
    EventType,
)
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.auth.domain.enums import UserRole
from modules.notifications.domain.enums import NotificationEntityType


# ============================================================
# HELPERS
# ============================================================

def make_current_admin(*, user_id="admin-1"):
    return Mock(
        id=user_id,
        role=UserRole.ADMIN,
    )


def make_user(
    *,
    user_id="user-1",
    first_name="leila",
    email="leila@example.com",
):
    return Mock(
        id=user_id,
        first_name=first_name,
        email=email,
    )


def make_application(
    *,
    application_id="application-1",
    user_id="user-1",
    vehicle_id="vehicle-1",
    status=ApplicationStatus.DRAFT,
    user=None,
):
    return Application(
        id=application_id,
        user_id=user_id,
        vehicle_id=vehicle_id,
        status=status,
        user=user or make_user(user_id=user_id),
    )


def make_notification(
    *,
    title="Statut de votre dossier",
    message="Votre dossier a été mis à jour.",
    notification_type="APPLICATION_STATUS",
):
    return Mock(
        title=title,
        message=message,
        type=notification_type,
    )


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def application_repository():
    return Mock()


@pytest.fixture
def notification_service():
    service = Mock()
    service.send = AsyncMock()
    return service


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def uow():
    return Mock()


@pytest.fixture
def use_case(
    application_repository,
    notification_service,
    event_service,
    uow,
):
    return UpdateApplicationStatusUseCase(
        application_repository=application_repository,
        notification_service=notification_service,
        event_service=event_service,
        uow=uow,
    )


@pytest.fixture
def current_admin():
    return make_current_admin()


@pytest.fixture
def dto():
    return UpdateApplicationStatusDTO(
        application_id="application-1",
        status=ApplicationStatus.APPROVED,
        reason="Dossier validé.",
    )


# ============================================================
# APPLICATION NOT FOUND
# ============================================================

@pytest.mark.asyncio
async def test_application_not_found(
    use_case,
    application_repository,
    notification_service,
    event_service,
    uow,
    dto,
    current_admin,
):
    application_repository.get_by_id.return_value = None

    with pytest.raises(ApplicationNotFound):
        await use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    application_repository.get_by_id.assert_called_once_with(
        "application-1"
    )

    application_repository.update.assert_not_called()
    notification_service.send.assert_not_awaited()
    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


# ============================================================
# STATUS UPDATE
# ============================================================

@pytest.mark.asyncio
async def test_application_status_is_updated(
    use_case,
    application_repository,
    dto,
    current_admin,
):
    application = make_application(
        status=ApplicationStatus.DRAFT,
    )

    application_repository.get_by_id.return_value = application

    notification = make_notification()

    with patch(
        "modules.applications.application.use_cases.admin.update_application_status."
        "ApplicationNotificationBuilder.build",
        return_value=notification,
    ):
        await use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    assert application.status == ApplicationStatus.APPROVED
    assert application.previous_status == ApplicationStatus.DRAFT


# ============================================================
# APPLICATION UPDATE
# ============================================================

@pytest.mark.asyncio
async def test_application_is_updated_in_repository(
    use_case,
    application_repository,
    dto,
    current_admin,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    notification = make_notification()

    with patch(
        "modules.applications.application.use_cases.admin.update_application_status."
        "ApplicationNotificationBuilder.build",
        return_value=notification,
    ):
        await use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    application_repository.update.assert_called_once_with(
        application
    )


# ============================================================
# NOTIFICATION BUILDER
# ============================================================

@pytest.mark.asyncio
async def test_notification_is_built_with_expected_arguments(
    use_case,
    application_repository,
    dto,
    current_admin,
):
    user = make_user(
        first_name="Marie",
        email="marie@example.com",
    )

    application = make_application(
        user=user,
    )

    application_repository.get_by_id.return_value = application

    notification = make_notification()

    with patch(
        "modules.applications.application.use_cases.admin.update_application_status."
        "ApplicationNotificationBuilder.build",
        return_value=notification,
    ) as build_mock:
        await use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    build_mock.assert_called_once_with(
        application=application,
        status=ApplicationStatus.APPROVED,
        reason="Dossier validé.",
        user_first_name="Marie",
    )


# ============================================================
# NOTIFICATION
# ============================================================

@pytest.mark.asyncio
async def test_notification_is_sent(
    use_case,
    application_repository,
    notification_service,
    dto,
    current_admin,
):
    user = make_user(
        email="client@example.com",
    )

    application = make_application(
        user=user,
    )

    application_repository.get_by_id.return_value = application

    notification = make_notification(
        title="Dossier approuvé",
        message="Votre dossier a été approuvé.",
        notification_type="APPLICATION_APPROVED",
    )

    with patch(
        "modules.applications.application.use_cases.admin.update_application_status."
        "ApplicationNotificationBuilder.build",
        return_value=notification,
    ):
        await use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    notification_service.send.assert_awaited_once_with(
        user_id="user-1",
        email="client@example.com",
        entity_type=NotificationEntityType.APPLICATION,
        entity_id="application-1",
        title="Dossier approuvé",
        message="Votre dossier a été approuvé.",
        notif_type="APPLICATION_APPROVED",
    )


# ============================================================
# EVENT
# ============================================================

@pytest.mark.asyncio
async def test_event_is_logged(
    use_case,
    application_repository,
    event_service,
    dto,
    current_admin,
):
    application = make_application(
        status=ApplicationStatus.DRAFT,
    )

    application_repository.get_by_id.return_value = application

    notification = make_notification(
        message="Votre dossier a été approuvé.",
    )

    with patch(
        "modules.applications.application.use_cases.admin.update_application_status."
        "ApplicationNotificationBuilder.build",
        return_value=notification,
    ):
        await use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    event_service.log.assert_called_once_with(
        application_id="application-1",
        vehicle_id="vehicle-1",
        type=(
            __import__(
                "modules.applications.domain.application_messages",
                fromlist=["APPLICATION_EVENT_MAP"],
            ).APPLICATION_EVENT_MAP[
                ApplicationStatus.APPROVED
            ]
        ),
        message="Votre dossier a été approuvé.",
        user_id="admin-1",
        event_metadata={
            "old_status": ApplicationStatus.DRAFT.value,
            "new_status": ApplicationStatus.APPROVED.value,
            "reason": "Dossier validé.",
        },
    )


# ============================================================
# EVENT WITH OLD STATUS = NONE
# ============================================================

@pytest.mark.asyncio
async def test_event_contains_none_when_old_status_is_none(
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

    notification = make_notification()

    with patch(
        "modules.applications.application.use_cases.admin.update_application_status."
        "ApplicationNotificationBuilder.build",
        return_value=notification,
    ):
        await use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    call_kwargs = event_service.log.call_args.kwargs

    assert call_kwargs["event_metadata"] == {
        "old_status": None,
        "new_status": ApplicationStatus.APPROVED.value,
        "reason": "Dossier validé.",
    }


# ============================================================
# COMMIT
# ============================================================

@pytest.mark.asyncio
async def test_commit_is_called(
    use_case,
    application_repository,
    uow,
    dto,
    current_admin,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    notification = make_notification()

    with patch(
        "modules.applications.application.use_cases.admin.update_application_status."
        "ApplicationNotificationBuilder.build",
        return_value=notification,
    ):
        await use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()


# ============================================================
# UPDATE ERROR
# ============================================================

@pytest.mark.asyncio
async def test_application_update_error_rolls_back(
    use_case,
    application_repository,
    notification_service,
    event_service,
    uow,
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
        await use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()

    notification_service.send.assert_not_awaited()
    event_service.log.assert_not_called()


# ============================================================
# NOTIFICATION ERROR
# ============================================================

@pytest.mark.asyncio
async def test_notification_error_rolls_back(
    use_case,
    application_repository,
    notification_service,
    event_service,
    uow,
    dto,
    current_admin,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    notification = make_notification()

    notification_service.send.side_effect = RuntimeError(
        "notification error"
    )

    with patch(
        "modules.applications.application.use_cases.admin.update_application_status."
        "ApplicationNotificationBuilder.build",
        return_value=notification,
    ):
        with pytest.raises(
            RuntimeError,
            match="notification error",
        ):
            await use_case.execute(
                dto=dto,
                current_admin=current_admin,
            )

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()

    event_service.log.assert_not_called()


# ============================================================
# EVENT ERROR
# ============================================================

@pytest.mark.asyncio
async def test_event_error_rolls_back(
    use_case,
    application_repository,
    notification_service,
    event_service,
    uow,
    dto,
    current_admin,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    notification = make_notification()

    event_service.log.side_effect = RuntimeError(
        "event error"
    )

    with patch(
        "modules.applications.application.use_cases.admin.update_application_status."
        "ApplicationNotificationBuilder.build",
        return_value=notification,
    ):
        with pytest.raises(
            RuntimeError,
            match="event error",
        ):
            await use_case.execute(
                dto=dto,
                current_admin=current_admin,
            )

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()


# ============================================================
# COMMIT ERROR
# ============================================================

@pytest.mark.asyncio
async def test_commit_error_rolls_back(
    use_case,
    application_repository,
    uow,
    dto,
    current_admin,
):
    application = make_application()

    application_repository.get_by_id.return_value = application

    notification = make_notification()

    uow.commit.side_effect = RuntimeError(
        "commit error"
    )

    with patch(
        "modules.applications.application.use_cases.admin.update_application_status."
        "ApplicationNotificationBuilder.build",
        return_value=notification,
    ):
        with pytest.raises(
            RuntimeError,
            match="commit error",
        ):
            await use_case.execute(
                dto=dto,
                current_admin=current_admin,
            )

    uow.commit.assert_called_once()
    uow.rollback.assert_called_once()


# ============================================================
# RESULT
# ============================================================

@pytest.mark.asyncio
async def test_returns_update_application_status_result(
    use_case,
    application_repository,
    dto,
    current_admin,
):
    application = make_application(
        status=ApplicationStatus.DRAFT,
    )

    application_repository.get_by_id.return_value = application

    notification = make_notification()

    with patch(
        "modules.applications.application.use_cases.admin.update_application_status."
        "ApplicationNotificationBuilder.build",
        return_value=notification,
    ):
        result = await use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    assert isinstance(
        result,
        UpdateApplicationStatusResult,
    )

    assert result.id == "application-1"
    assert result.status == ApplicationStatus.APPROVED


# ============================================================
# RESULT STATUS MATCHES APPLICATION
# ============================================================

@pytest.mark.asyncio
async def test_result_contains_new_application_status(
    use_case,
    application_repository,
    dto,
    current_admin,
):
    application = make_application(
        status=ApplicationStatus.DRAFT,
    )

    application_repository.get_by_id.return_value = application

    notification = make_notification()

    with patch(
        "modules.applications.application.use_cases.admin.update_application_status."
        "ApplicationNotificationBuilder.build",
        return_value=notification,
    ):
        result = await use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    assert result.status == application.status
    assert result.status == ApplicationStatus.APPROVED