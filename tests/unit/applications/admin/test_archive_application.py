from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from modules.applications.application.dtos.application_id_dto import (
    ApplicationIdDTO,
)
from modules.applications.application.use_cases.admin.archive_application import (
    ArchiveApplicationUseCase,
)
from modules.applications.domain.enums import (
    ApplicationStatus,
    EventType,
)
from modules.applications.domain.exceptions import (
    ApplicationAlreadyArchived,
    ApplicationNotFound,
    CannotArchiveApplication,
)
from modules.applications.domain.policies.archive_application_policy import (
    ArchiveApplicationPolicy,
)


# ============================================================
# HELPERS
# ============================================================

def create_application(
    *,
    application_id="application-1",
    vehicle_id="vehicle-1",
    status=ApplicationStatus.CANCELLED,
    is_archived=False,
    deleted_at=None,
):
    """
    Crée un objet application minimal pour les tests.

    On utilise SimpleNamespace car les tests portent ici sur
    le comportement du use case et de la policy, pas sur le
    mapping SQLAlchemy.
    """
    return SimpleNamespace(
        id=application_id,
        vehicle_id=vehicle_id,
        status=status,
        is_archived=is_archived,
        deleted_at=deleted_at,
    )


def create_use_case():
    application_repository = Mock()
    event_service = Mock()
    unit_of_work = Mock()

    use_case = ArchiveApplicationUseCase(
        application_repository=application_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )

    return (
        use_case,
        application_repository,
        event_service,
        unit_of_work,
    )


def create_dto(application_id="application-1"):
    return ApplicationIdDTO(
        application_id=application_id,
    )


def create_admin(admin_id="admin-1"):
    return SimpleNamespace(
        id=admin_id,
    )


# ============================================================
# ARCHIVE APPLICATION POLICY
# ============================================================

class TestArchiveApplicationPolicy:

    def test_can_archive_returns_true_for_allowed_status(self):
        application = create_application(
            status=ApplicationStatus.CANCELLED,
        )

        assert ArchiveApplicationPolicy.can_archive(application) is True

    def test_can_archive_returns_false_when_application_is_deleted(self):
        application = create_application(
            deleted_at=datetime.now(timezone.utc),
        )

        assert ArchiveApplicationPolicy.can_archive(application) is False

    def test_can_archive_returns_false_when_application_is_already_archived(self):
        application = create_application(
            is_archived=True,
        )

        assert ArchiveApplicationPolicy.can_archive(application) is False

    def test_can_archive_returns_false_for_disallowed_status(self):
        application = create_application(
            status=ApplicationStatus.DRAFT,
        )

        assert ArchiveApplicationPolicy.can_archive(application) is False

    def test_validate_rejects_deleted_application(self):
        application = create_application(
            deleted_at=datetime.now(timezone.utc),
        )

        with pytest.raises(CannotArchiveApplication) as exc_info:
            ArchiveApplicationPolicy.validate(application)

        assert (
            str(exc_info.value)
            == "Un dossier supprimé ne peut pas être archivé."
        )

    def test_validate_rejects_already_archived_application(self):
        application = create_application(
            is_archived=True,
        )

        with pytest.raises(ApplicationAlreadyArchived):
            ArchiveApplicationPolicy.validate(application)

    @pytest.mark.parametrize(
        "status",
        [
            ApplicationStatus.CANCELLED,
            ApplicationStatus.COMPLETED,
            ApplicationStatus.REJECTED,
        ],
    )
    def test_validate_accepts_allowed_statuses(self, status):
        application = create_application(
            status=status,
        )

        # Ne doit lever aucune exception
        ArchiveApplicationPolicy.validate(application)

    def test_validate_rejects_disallowed_status(self):
        application = create_application(
            status=ApplicationStatus.DRAFT,
        )

        with pytest.raises(CannotArchiveApplication) as exc_info:
            ArchiveApplicationPolicy.validate(application)

        assert (
            str(exc_info.value)
            == "Ce dossier ne peut pas être archivé "
            "dans son état actuel."
        )


# ============================================================
# ARCHIVE APPLICATION USE CASE
# ============================================================

class TestArchiveApplicationUseCase:

    def test_execute_raises_application_not_found(self):
        (
            use_case,
            application_repository,
            event_service,
            unit_of_work,
        ) = create_use_case()

        application_repository.get_by_id.return_value = None

        dto = create_dto()
        admin = create_admin()

        with pytest.raises(ApplicationNotFound):
            use_case.execute(dto, admin)

        application_repository.get_by_id.assert_called_once_with(
            "application-1"
        )

        unit_of_work.rollback.assert_called_once()

        event_service.log.assert_not_called()
        unit_of_work.commit.assert_not_called()
        application_repository.update.assert_not_called()

    def test_execute_archives_application_successfully(self):
        (
            use_case,
            application_repository,
            event_service,
            unit_of_work,
        ) = create_use_case()

        application = create_application(
            status=ApplicationStatus.CANCELLED,
        )

        application_repository.get_by_id.return_value = application

        dto = create_dto()
        admin = create_admin()

        result = use_case.execute(dto, admin)

        # Application archivée
        assert result is application
        assert application.is_archived is True

        # Repository
        application_repository.get_by_id.assert_called_once_with(
            "application-1"
        )

        application_repository.update.assert_called_once_with(
            application
        )

        # Commit
        unit_of_work.commit.assert_called_once()
        unit_of_work.rollback.assert_not_called()

        # Event
        event_service.log.assert_called_once_with(
            application_id="application-1",
            user_id="admin-1",
            vehicle_id="vehicle-1",
            type=EventType.APPLICATION_ARCHIVED,
            message="Dossier archivé par administrateur.",
            event_metadata={
                "archived_by": "admin-1",
                "vehicle_id": "vehicle-1",
                "status_before": ApplicationStatus.CANCELLED.value,
            },
        )

    def test_execute_rejects_already_archived_application(self):
        (
            use_case,
            application_repository,
            event_service,
            unit_of_work,
        ) = create_use_case()

        application = create_application(
            is_archived=True,
        )

        application_repository.get_by_id.return_value = application

        dto = create_dto()
        admin = create_admin()

        with pytest.raises(ApplicationAlreadyArchived):
            use_case.execute(dto, admin)

        # L'application ne doit pas être modifiée
        assert application.is_archived is True

        application_repository.update.assert_not_called()
        event_service.log.assert_not_called()

        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    def test_execute_rejects_deleted_application(self):
        (
            use_case,
            application_repository,
            event_service,
            unit_of_work,
        ) = create_use_case()

        application = create_application(
            deleted_at=datetime.now(timezone.utc),
        )

        application_repository.get_by_id.return_value = application

        dto = create_dto()
        admin = create_admin()

        with pytest.raises(CannotArchiveApplication) as exc_info:
            use_case.execute(dto, admin)

        assert (
            str(exc_info.value)
            == "Un dossier supprimé ne peut pas être archivé."
        )

        application_repository.update.assert_not_called()
        event_service.log.assert_not_called()

        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    def test_execute_rejects_application_with_disallowed_status(self):
        (
            use_case,
            application_repository,
            event_service,
            unit_of_work,
        ) = create_use_case()

        application = create_application(
            status=ApplicationStatus.DRAFT,
        )

        application_repository.get_by_id.return_value = application

        dto = create_dto()
        admin = create_admin()

        with pytest.raises(CannotArchiveApplication) as exc_info:
            use_case.execute(dto, admin)

        assert (
            str(exc_info.value)
            == "Ce dossier ne peut pas être archivé "
            "dans son état actuel."
        )

        # La policy doit empêcher toute modification
        assert application.is_archived is False

        application_repository.update.assert_not_called()
        event_service.log.assert_not_called()

        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    @pytest.mark.parametrize(
        "status",
        [
            ApplicationStatus.CANCELLED,
            ApplicationStatus.COMPLETED,
            ApplicationStatus.REJECTED,
        ],
    )
    def test_execute_archives_application_for_each_allowed_status(
        self,
        status,
    ):
        (
            use_case,
            application_repository,
            event_service,
            unit_of_work,
        ) = create_use_case()

        application = create_application(
            status=status,
        )

        application_repository.get_by_id.return_value = application

        dto = create_dto()
        admin = create_admin()

        result = use_case.execute(dto, admin)

        assert result is application
        assert application.is_archived is True

        application_repository.update.assert_called_once_with(
            application
        )

        event_service.log.assert_called_once()

        unit_of_work.commit.assert_called_once()
        unit_of_work.rollback.assert_not_called()

    def test_execute_rolls_back_when_repository_update_fails(self):
        (
            use_case,
            application_repository,
            event_service,
            unit_of_work,
        ) = create_use_case()

        application = create_application(
            status=ApplicationStatus.CANCELLED,
        )

        application_repository.get_by_id.return_value = application

        application_repository.update.side_effect = Exception(
            "Database error"
        )

        dto = create_dto()
        admin = create_admin()

        with pytest.raises(Exception, match="Database error"):
            use_case.execute(dto, admin)

        assert application.is_archived is True

        application_repository.update.assert_called_once_with(
            application
        )

        event_service.log.assert_not_called()
        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    def test_execute_rolls_back_when_event_logging_fails(self):
        (
            use_case,
            application_repository,
            event_service,
            unit_of_work,
        ) = create_use_case()

        application = create_application(
            status=ApplicationStatus.CANCELLED,
        )

        application_repository.get_by_id.return_value = application

        event_service.log.side_effect = Exception(
            "Event error"
        )

        dto = create_dto()
        admin = create_admin()

        with pytest.raises(Exception, match="Event error"):
            use_case.execute(dto, admin)

        assert application.is_archived is True

        application_repository.update.assert_called_once_with(
            application
        )

        event_service.log.assert_called_once()

        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    def test_execute_rolls_back_when_commit_fails(self):
        (
            use_case,
            application_repository,
            event_service,
            unit_of_work,
        ) = create_use_case()

        application = create_application(
            status=ApplicationStatus.CANCELLED,
        )

        application_repository.get_by_id.return_value = application

        unit_of_work.commit.side_effect = Exception(
            "Commit error"
        )

        dto = create_dto()
        admin = create_admin()

        with pytest.raises(Exception, match="Commit error"):
            use_case.execute(dto, admin)

        assert application.is_archived is True

        application_repository.update.assert_called_once_with(
            application
        )

        event_service.log.assert_called_once()

        unit_of_work.commit.assert_called_once()
        unit_of_work.rollback.assert_called_once()
