from unittest.mock import Mock

import pytest

from modules.auth.application.use_cases.admin.archive_users import (
    ArchiveUsersUseCase,
)
from modules.auth.application.dtos.admin.archive_users_dto import (
    ArchiveUsersDTO,
)
from modules.auth.domain.entities.user import User
from modules.auth.domain.enums import UserRole
from modules.auth.domain.exceptions import (
    CannotArchiveAdmin,
    InvalidUserIds,
    UserAlreadyArchived,
)
from modules.applications.domain.enums import EventType


def create_user(
    user_id: str,
    role: UserRole = UserRole.CLIENT,
    is_deleted: bool = False,
) -> User:
    return User(
        id=user_id,
        first_name="Leila",
        last_name="El",
        email=f"{user_id}@example.com",
        password="hashed-password",
        role=role,
        is_verified=True,
        is_active=True,
        accepted_cgu=True,
        is_deleted=is_deleted,
        deleted_at=None,
    )


def create_dto(
    user_ids: list[str],
) -> ArchiveUsersDTO:
    return ArchiveUsersDTO(
        user_ids=user_ids,
    )


def test_archive_users_success():
    user_repo = Mock()
    event_service = Mock()
    uow = Mock()

    user1 = create_user("user-1")
    user2 = create_user("user-2")

    user_repo.find_by_ids.return_value = [
        user1,
        user2,
    ]

    dto = create_dto(
        ["user-1", "user-2"]
    )

    use_case = ArchiveUsersUseCase(
        user_repo=user_repo,
        event_service=event_service,
        uow=uow,
    )

    result = use_case.execute(
        dto=dto,
        admin_id="admin-123",
    )

    # Résultat
    assert result.archived_count == 2
    assert result.user_ids == [
        "user-1",
        "user-2",
    ]

    # Vérification de l'archivage
    assert user1.is_deleted is True
    assert user1.is_active is False
    assert user1.deleted_at is not None

    assert user2.is_deleted is True
    assert user2.is_active is False
    assert user2.deleted_at is not None

    # Repository
    user_repo.find_by_ids.assert_called_once_with(
        ["user-1", "user-2"]
    )

    assert user_repo.update.call_count == 2

    user_repo.update.assert_any_call(user1)
    user_repo.update.assert_any_call(user2)

    # Event
    event_service.log.assert_called_once()

    event = event_service.log.call_args.kwargs

    assert event["type"] == EventType.ADMIN_ACTION
    assert event["message"] == (
        "Archivage de plusieurs utilisateurs"
    )
    assert event["user_id"] == "admin-123"

    assert event["event_metadata"] == {
        "action": "archive_users",
        "user_ids": [
            "user-1",
            "user-2",
        ],
        "count": 2,
    }

    # Transaction
    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()


def test_archive_users_invalid_when_user_ids_empty():
    user_repo = Mock()
    event_service = Mock()
    uow = Mock()

    dto = create_dto([])

    use_case = ArchiveUsersUseCase(
        user_repo=user_repo,
        event_service=event_service,
        uow=uow,
    )

    with pytest.raises(InvalidUserIds):
        use_case.execute(
            dto=dto,
            admin_id="admin-123",
        )

    user_repo.find_by_ids.assert_not_called()
    user_repo.update.assert_not_called()
    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_archive_users_invalid_when_some_users_are_missing():
    user_repo = Mock()
    event_service = Mock()
    uow = Mock()

    user1 = create_user("user-1")

    user_repo.find_by_ids.return_value = [
        user1,
    ]

    dto = create_dto(
        [
            "user-1",
            "user-2",
        ]
    )

    use_case = ArchiveUsersUseCase(
        user_repo=user_repo,
        event_service=event_service,
        uow=uow,
    )

    with pytest.raises(
        InvalidUserIds,
        match="Certains utilisateurs sont introuvables",
    ):
        use_case.execute(
            dto=dto,
            admin_id="admin-123",
        )

    user_repo.find_by_ids.assert_called_once_with(
        [
            "user-1",
            "user-2",
        ]
    )

    user_repo.update.assert_not_called()
    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_archive_users_cannot_archive_admin():
    user_repo = Mock()
    event_service = Mock()
    uow = Mock()

    user1 = create_user("user-1")
    admin = create_user(
        "admin-1",
        role=UserRole.ADMIN,
    )

    user_repo.find_by_ids.return_value = [
        user1,
        admin,
    ]

    dto = create_dto(
        [
            "user-1",
            "admin-1",
        ]
    )

    use_case = ArchiveUsersUseCase(
        user_repo=user_repo,
        event_service=event_service,
        uow=uow,
    )

    with pytest.raises(
        CannotArchiveAdmin,
        match="Impossible d'archiver l'administrateur admin-1"
    ):
        use_case.execute(
            dto=dto,
            admin_id="admin-123",
        )

    # Aucun utilisateur ne doit avoir été archivé
    assert user1.is_deleted is False
    assert user1.is_active is True

    assert admin.is_deleted is False
    assert admin.is_active is True

    user_repo.update.assert_not_called()
    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_archive_users_cannot_archive_already_archived_user():
    user_repo = Mock()
    event_service = Mock()
    uow = Mock()

    user1 = create_user(
        "user-1",
        is_deleted=True,
    )

    user_repo.find_by_ids.return_value = [
        user1,
    ]

    dto = create_dto(
        ["user-1"]
    )

    use_case = ArchiveUsersUseCase(
        user_repo=user_repo,
        event_service=event_service,
        uow=uow,
    )

    with pytest.raises(
        UserAlreadyArchived,
        match="Utilisateur user-1 déjà archivé",
    ):
        use_case.execute(
            dto=dto,
            admin_id="admin-123",
        )

    user_repo.update.assert_not_called()
    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_archive_users_rollback_when_update_fails():
    user_repo = Mock()
    event_service = Mock()
    uow = Mock()

    user1 = create_user("user-1")
    user2 = create_user("user-2")

    user_repo.find_by_ids.return_value = [
        user1,
        user2,
    ]

    user_repo.update.side_effect = RuntimeError(
        "Database error"
    )

    dto = create_dto(
        [
            "user-1",
            "user-2",
        ]
    )

    use_case = ArchiveUsersUseCase(
        user_repo=user_repo,
        event_service=event_service,
        uow=uow,
    )

    with pytest.raises(
        RuntimeError,
        match="Database error",
    ):
        use_case.execute(
            dto=dto,
            admin_id="admin-123",
        )

    user_repo.find_by_ids.assert_called_once()

    user_repo.update.assert_called_once_with(
        user1
    )

    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_archive_users_rollback_when_event_logging_fails():
    user_repo = Mock()
    event_service = Mock()
    uow = Mock()

    user1 = create_user("user-1")
    user2 = create_user("user-2")

    user_repo.find_by_ids.return_value = [
        user1,
        user2,
    ]

    event_service.log.side_effect = RuntimeError(
        "Event logging error"
    )

    dto = create_dto(
        [
            "user-1",
            "user-2",
        ]
    )

    use_case = ArchiveUsersUseCase(
        user_repo=user_repo,
        event_service=event_service,
        uow=uow,
    )

    with pytest.raises(
        RuntimeError,
        match="Event logging error",
    ):
        use_case.execute(
            dto=dto,
            admin_id="admin-123",
        )

    # Les utilisateurs ont bien été préparés et envoyés
    # au repository avant l'erreur sur l'événement.
    assert user_repo.update.call_count == 2

    user_repo.update.assert_any_call(user1)
    user_repo.update.assert_any_call(user2)

    event_service.log.assert_called_once()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()