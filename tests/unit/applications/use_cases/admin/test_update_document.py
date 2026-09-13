from unittest.mock import AsyncMock, Mock, patch

import pytest

from modules.applications.application.dtos.admin.update_document_dto import (
    UpdateDocumentDTO,
)
from modules.applications.application.results.admin.update_document_result import (
    UpdateDocumentResult,
)
from modules.applications.application.use_cases.admin.update_document import (
    UpdateDocumentUseCase,
)
from modules.applications.domain.document_messages import (
    DOCUMENT_EVENT_MAP,
)
from modules.applications.domain.enums import DocumentStatus
from modules.applications.domain.exceptions import (
    ApplicationNotFound,
    DocumentNotFound,
)
from modules.notifications.domain.enums import (
    NotificationEntityType,
    NotificationType,
)


# ============================================================
# HELPERS
# ============================================================

def make_admin(*, admin_id="admin-1"):
    return Mock(id=admin_id)


def make_document(
    *,
    document_id="document-1",
    application_id="application-1",
    document_type="IDENTITY",
    status=DocumentStatus.PENDING,
    comment=None,
):
    document = Mock(
        id=document_id,
        application_id=application_id,
        type=document_type,
        status=status,
        comment=comment,
    )

    def update_status(*, status, comment):
        document.status = status
        document.comment = comment

    document.update_status = Mock(
        side_effect=update_status,
    )

    return document


def make_user(
    *,
    user_id="user-1",
    email="client@example.com",
):
    return Mock(
        id=user_id,
        email=email,
    )


def make_application(
    *,
    application_id="application-1",
    user_id="user-1",
    vehicle_id="vehicle-1",
    user=None,
):
    return Mock(
        id=application_id,
        user_id=user_id,
        vehicle_id=vehicle_id,
        user=user or make_user(user_id=user_id),
    )


def make_notification(
    *,
    title="Document refusé",
    message="Votre document a été refusé.",
    notification_type=NotificationType.DOCUMENT_REJECTED,
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
def document_repository():
    return Mock()


@pytest.fixture
def application_repository():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def notification_service():
    service = Mock()
    service.send = AsyncMock()
    return service


@pytest.fixture
def uow():
    return Mock()


@pytest.fixture
def use_case(
    document_repository,
    application_repository,
    event_service,
    notification_service,
    uow,
):
    return UpdateDocumentUseCase(
        document_repository=document_repository,
        application_repository=application_repository,
        event_service=event_service,
        notification_service=notification_service,
        uow=uow,
    )


@pytest.fixture
def current_admin():
    return make_admin()


@pytest.fixture
def dto():
    return UpdateDocumentDTO(
        document_id="document-1",
        status=DocumentStatus.VALIDATED,
        comment="Document validé.",
    )


# ============================================================
# DOCUMENT NOT FOUND
# ============================================================

@pytest.mark.asyncio
async def test_document_not_found(
    use_case,
    document_repository,
    application_repository,
    event_service,
    notification_service,
    uow,
    dto,
    current_admin,
):
    document_repository.get_by_id.return_value = None

    with pytest.raises(DocumentNotFound):
        await use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    document_repository.get_by_id.assert_called_once_with(
        "document-1"
    )

    application_repository.get_by_id.assert_not_called()
    document_repository.save.assert_not_called()
    event_service.log.assert_not_called()
    notification_service.send.assert_not_awaited()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


# ============================================================
# APPLICATION NOT FOUND
# ============================================================

@pytest.mark.asyncio
async def test_application_not_found(
    use_case,
    document_repository,
    application_repository,
    event_service,
    notification_service,
    uow,
    dto,
    current_admin,
):
    document = make_document()

    document_repository.get_by_id.return_value = document
    application_repository.get_by_id.return_value = None

    with pytest.raises(ApplicationNotFound):
        await use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    document_repository.get_by_id.assert_called_once_with(
        "document-1"
    )

    application_repository.get_by_id.assert_called_once_with(
        "application-1"
    )

    document.update_status.assert_not_called()
    document_repository.save.assert_not_called()
    event_service.log.assert_not_called()
    notification_service.send.assert_not_awaited()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


# ============================================================
# DOCUMENT STATUS UPDATE
# ============================================================

@pytest.mark.asyncio
async def test_document_status_is_updated(
    use_case,
    document_repository,
    application_repository,
    dto,
    current_admin,
):
    document = make_document(
        status=DocumentStatus.PENDING,
    )
    application = make_application()

    document_repository.get_by_id.return_value = document
    application_repository.get_by_id.return_value = application

    with patch(
        "modules.applications.application.use_cases.admin.update_document."
        "DocumentMessageBuilder.build",
        return_value="Document validé.",
    ):
        await use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    document.update_status.assert_called_once_with(
        status=DocumentStatus.VALIDATED,
        comment="Document validé.",
    )

    assert document.status == DocumentStatus.VALIDATED
    assert document.comment == "Document validé."


# ============================================================
# DOCUMENT SAVE
# ============================================================

@pytest.mark.asyncio
async def test_document_is_saved(
    use_case,
    document_repository,
    application_repository,
    dto,
    current_admin,
):
    document = make_document()
    application = make_application()

    document_repository.get_by_id.return_value = document
    application_repository.get_by_id.return_value = application

    with patch(
        "modules.applications.application.use_cases.admin.update_document."
        "DocumentMessageBuilder.build",
        return_value="Document validé.",
    ):
        await use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    document_repository.save.assert_called_once_with(
        document
    )


# ============================================================
# EVENT
# ============================================================

@pytest.mark.asyncio
async def test_document_event_is_logged(
    use_case,
    document_repository,
    application_repository,
    event_service,
    dto,
    current_admin,
):
    document = make_document(
        document_type="ID_CARD",
    )
    application = make_application()

    document_repository.get_by_id.return_value = document
    application_repository.get_by_id.return_value = application

    with patch(
        "modules.applications.application.use_cases.admin.update_document."
        "DocumentMessageBuilder.build",
        return_value="Votre pièce d'identité a été validée.",
    ):
        await use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    event_service.log.assert_called_once_with(
        application_id="application-1",
        type=DOCUMENT_EVENT_MAP[DocumentStatus.VALIDATED],
        message="Votre pièce d'identité a été validée.",
        user_id="admin-1",
        vehicle_id="vehicle-1",
        event_metadata={
            "document_id": "document-1",
            "document_type": "ID_CARD",
            "status": DocumentStatus.VALIDATED.value,
        },
    )


# ============================================================
# REJECTED NOTIFICATION
# ============================================================

@pytest.mark.asyncio
async def test_rejected_document_sends_notification(
    use_case,
    document_repository,
    application_repository,
    notification_service,
    dto,
    current_admin,
):
    rejected_dto = UpdateDocumentDTO(
        document_id="document-1",
        status=DocumentStatus.REJECTED,
        comment="Document illisible.",
    )

    user = make_user(
        user_id="user-1",
        email="client@example.com",
    )

    document = make_document(
        document_type="ID_CARD",
    )
    application = make_application(
        user=user,
    )

    document_repository.get_by_id.return_value = document
    application_repository.get_by_id.return_value = application

    notification = make_notification(
        title="Document refusé",
        message="Votre pièce d'identité est illisible.",
    )

    with patch(
        "modules.applications.application.use_cases.admin.update_document."
        "DocumentMessageBuilder.build",
        return_value="Document refusé.",
    ), patch(
        "modules.applications.application.use_cases.admin.update_document."
        "DocumentNotificationBuilder.build_rejected",
        return_value=notification,
    ) as notification_builder:
        await use_case.execute(
            dto=rejected_dto,
            current_admin=current_admin,
        )

    notification_builder.assert_called_once_with(
        document_type="ID_CARD",
        comment="Document illisible.",
    )

    notification_service.send.assert_awaited_once_with(
        user_id="user-1",
        email="client@example.com",
        entity_type=NotificationEntityType.APPLICATION,
        entity_id="application-1",
        title="Document refusé",
        message="Votre pièce d'identité est illisible.",
        notif_type=NotificationType.DOCUMENT_REJECTED,
    )


# ============================================================
# NON REJECTED = NO NOTIFICATION
# ============================================================

@pytest.mark.parametrize(
    "status",
    [
        DocumentStatus.PENDING,
        DocumentStatus.VALIDATED,
    ],
)
@pytest.mark.asyncio
async def test_non_rejected_document_does_not_send_notification(
    status,
    use_case,
    document_repository,
    application_repository,
    notification_service,
    dto,
    current_admin,
):
    update_dto = UpdateDocumentDTO(
        document_id="document-1",
        status=status,
        comment="Mise à jour.",
    )

    document = make_document()
    application = make_application()

    document_repository.get_by_id.return_value = document
    application_repository.get_by_id.return_value = application

    with patch(
        "modules.applications.application.use_cases.admin.update_document."
        "DocumentMessageBuilder.build",
        return_value="Document mis à jour.",
    ), patch(
        "modules.applications.application.use_cases.admin.update_document."
        "DocumentNotificationBuilder.build_rejected",
    ) as notification_builder:

        await use_case.execute(
            dto=update_dto,
            current_admin=current_admin,
        )

    notification_builder.assert_not_called()


# ============================================================
# COMMIT
# ============================================================

@pytest.mark.asyncio
async def test_commit_is_called(
    use_case,
    document_repository,
    application_repository,
    uow,
    dto,
    current_admin,
):
    document = make_document()
    application = make_application()

    document_repository.get_by_id.return_value = document
    application_repository.get_by_id.return_value = application

    with patch(
        "modules.applications.application.use_cases.admin.update_document."
        "DocumentMessageBuilder.build",
        return_value="Document validé.",
    ):
        await use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()


# ============================================================
# SAVE ERROR
# ============================================================

@pytest.mark.asyncio
async def test_document_save_error_rolls_back(
    use_case,
    document_repository,
    application_repository,
    event_service,
    notification_service,
    uow,
    dto,
    current_admin,
):
    document = make_document()
    application = make_application()

    document_repository.get_by_id.return_value = document
    application_repository.get_by_id.return_value = application

    document_repository.save.side_effect = RuntimeError(
        "save error"
    )

    with pytest.raises(
        RuntimeError,
        match="save error",
    ):
        await use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()

    event_service.log.assert_not_called()
    notification_service.send.assert_not_awaited()


# ============================================================
# EVENT ERROR
# ============================================================

@pytest.mark.asyncio
async def test_event_error_rolls_back(
    use_case,
    document_repository,
    application_repository,
    event_service,
    notification_service,
    uow,
    dto,
    current_admin,
):
    document = make_document()
    application = make_application()

    document_repository.get_by_id.return_value = document
    application_repository.get_by_id.return_value = application

    event_service.log.side_effect = RuntimeError(
        "event error"
    )

    with patch(
        "modules.applications.application.use_cases.admin.update_document."
        "DocumentMessageBuilder.build",
        return_value="Document validé.",
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
    notification_service.send.assert_not_awaited()


# ============================================================
# NOTIFICATION ERROR
# ============================================================

@pytest.mark.asyncio
async def test_notification_error_rolls_back(
    use_case,
    document_repository,
    application_repository,
    notification_service,
    event_service,
    uow,
    current_admin,
):
    dto = UpdateDocumentDTO(
        document_id="document-1",
        status=DocumentStatus.REJECTED,
        comment="Document illisible.",
    )

    document = make_document()
    application = make_application()

    document_repository.get_by_id.return_value = document
    application_repository.get_by_id.return_value = application

    notification = make_notification()

    notification_service.send.side_effect = RuntimeError(
        "notification error"
    )

    with patch(
        "modules.applications.application.use_cases.admin.update_document."
        "DocumentMessageBuilder.build",
        return_value="Document refusé.",
    ), patch(
        "modules.applications.application.use_cases.admin.update_document."
        "DocumentNotificationBuilder.build_rejected",
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


# ============================================================
# COMMIT ERROR
# ============================================================

@pytest.mark.asyncio
async def test_commit_error_rolls_back(
    use_case,
    document_repository,
    application_repository,
    uow,
    dto,
    current_admin,
):
    document = make_document()
    application = make_application()

    document_repository.get_by_id.return_value = document
    application_repository.get_by_id.return_value = application

    uow.commit.side_effect = RuntimeError(
        "commit error"
    )

    with patch(
        "modules.applications.application.use_cases.admin.update_document."
        "DocumentMessageBuilder.build",
        return_value="Document validé.",
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
async def test_returns_update_document_result(
    use_case,
    document_repository,
    application_repository,
    dto,
    current_admin,
):
    document = make_document(
        status=DocumentStatus.PENDING,
        comment=None,
    )
    application = make_application()

    document_repository.get_by_id.return_value = document
    application_repository.get_by_id.return_value = application

    with patch(
        "modules.applications.application.use_cases.admin.update_document."
        "DocumentMessageBuilder.build",
        return_value="Document validé.",
    ):
        result = await use_case.execute(
            dto=dto,
            current_admin=current_admin,
        )

    assert isinstance(
        result,
        UpdateDocumentResult,
    )

    assert result.document_id == "document-1"
    assert result.status == DocumentStatus.VALIDATED
    assert result.comment == "Document validé."


# ============================================================
# RESULT AFTER REJECTION
# ============================================================

@pytest.mark.asyncio
async def test_rejected_document_result_contains_new_status_and_comment(
    use_case,
    document_repository,
    application_repository,
    dto,
    current_admin,
):
    rejected_dto = UpdateDocumentDTO(
        document_id="document-1",
        status=DocumentStatus.REJECTED,
        comment="Document illisible.",
    )

    document = make_document(
        status=DocumentStatus.PENDING,
    )
    application = make_application()

    document_repository.get_by_id.return_value = document
    application_repository.get_by_id.return_value = application

    notification = make_notification()

    with patch(
        "modules.applications.application.use_cases.admin.update_document."
        "DocumentMessageBuilder.build",
        return_value="Document refusé.",
    ), patch(
        "modules.applications.application.use_cases.admin.update_document."
        "DocumentNotificationBuilder.build_rejected",
        return_value=notification,
    ):
        result = await use_case.execute(
            dto=rejected_dto,
            current_admin=current_admin,
        )

    assert result.document_id == "document-1"
    assert result.status == DocumentStatus.REJECTED
    assert result.comment == "Document illisible."