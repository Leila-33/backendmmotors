from modules.applications.domain.entities.application import Application
from modules.applications.domain.enums import ApplicationStatus
from modules.applications.domain.exceptions import (
    ApplicationAlreadyArchived,
    CannotArchiveApplication,
)


class ArchiveApplicationPolicy:

    @staticmethod
    def can_archive(
        application: Application,
    ) -> bool:

        try:
            ArchiveApplicationPolicy.validate(
                application
            )

            return True

        except (
            CannotArchiveApplication,
            ApplicationAlreadyArchived,
        ):
            return False

    @staticmethod
    def validate(
        application: Application,
    ) -> None:

        # =====================================================
        # ALREADY DELETED
        # =====================================================

        if application.deleted_at is not None:
            raise CannotArchiveApplication(
                "Un dossier supprimé ne peut pas être archivé."
            )

        # =====================================================
        # ALREADY ARCHIVED
        # =====================================================

        if application.is_archived:
            raise ApplicationAlreadyArchived()

        # =====================================================
        # ALLOWED STATUS
        # =====================================================

        allowed_statuses = (
            ApplicationStatus.CANCELLED,
            ApplicationStatus.COMPLETED,
            ApplicationStatus.REJECTED,
        )

        if application.status not in allowed_statuses:
            raise CannotArchiveApplication(
                "Ce dossier ne peut pas être archivé "
                "dans son état actuel."
            )