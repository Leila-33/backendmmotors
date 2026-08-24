import logging
from datetime import datetime, timezone

from modules.applications.domain.enums import EventType
from modules.auth.application.results.admin.archive_users_result import (
    ArchiveUsersResult,
)
from modules.auth.domain.enums import UserRole
from modules.auth.domain.exceptions import (
    CannotArchiveAdmin,
    InvalidUserIds,
    UserAlreadyArchived,
)
from modules.auth.application.dtos.admin.archive_users_dto import (
    ArchiveUsersDTO,
)
logger = logging.getLogger(__name__)


class ArchiveUsersUseCase:

    def __init__(
        self,
        user_repo,
        event_service,
        uow,
    ):
        self.user_repo = user_repo
        self.event_service = event_service
        self.uow = uow

    def execute(
        self,
        dto: ArchiveUsersDTO,
        admin_id: str,
    ) -> ArchiveUsersResult:

        try:

            # =====================================================
            # VALIDATION
            # =====================================================

            if not dto.user_ids:
                raise InvalidUserIds()

            users = self.user_repo.find_by_ids(
                dto.user_ids
            )

            if len(users) != len(dto.user_ids):
                raise InvalidUserIds(
                    "Certains utilisateurs sont introuvables"
                )

            # =====================================================
            # BUSINESS RULES
            # =====================================================

            for user in users:

                if user.is_deleted:
                    raise UserAlreadyArchived(
                        f"Utilisateur {user.id} déjà archivé"
                    )

                if user.role == UserRole.ADMIN:
                    raise CannotArchiveAdmin()

            # =====================================================
            # ARCHIVE
            # =====================================================

            for user in users:

                user.archive()

                self.user_repo.update(user)

            # =====================================================
            # EVENT
            # =====================================================

            self.event_service.log(
                type=EventType.ADMIN_ACTION,
                message="Archivage de plusieurs utilisateurs",
                user_id=admin_id,
                event_metadata={
                    "action": "archive_users",
                    "user_ids": dto.user_ids,
                    "count": len(users),
                },
            )

            # =====================================================
            # COMMIT
            # =====================================================

            self.uow.commit()

            logger.info(
                "Archivage utilisateurs en masse effectué",
                extra={
                    "count": len(users),
                    "admin_id": admin_id,
                },
            )

            # =====================================================
            # RESULT
            # =====================================================

            return ArchiveUsersResult(
                archived_count=len(users),
                user_ids=[
                    user.id
                    for user in users
                ],
            )

        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur archivage utilisateurs en masse",
                extra={
                    "admin_id": admin_id,
                    "user_ids": dto.user_ids,
                },
            )

            raise