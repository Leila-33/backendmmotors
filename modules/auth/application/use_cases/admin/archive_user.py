import logging

from modules.applications.domain.enums import EventType
from modules.auth.domain.enums import UserRole
from modules.auth.domain.exceptions import (
    CannotArchiveAdmin,
    UserNotFound,
)
from modules.auth.application.results.admin.archive_user_result import ArchiveUserResult

logger = logging.getLogger(__name__)


class ArchiveUserUseCase:

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
        user_id: str,
        admin_id: str,
    ):

        try:

            # =====================================================
            # GET USER
            # =====================================================

            user = self.user_repo.get_by_id(
                user_id
            )

            if not user:
                raise UserNotFound()

            # =====================================================
            # BUSINESS RULE
            # =====================================================

            if user.role == UserRole.ADMIN:
                raise CannotArchiveAdmin(admin_id)

            # =====================================================
            # ARCHIVE
            # =====================================================

            user.archive()

            self.user_repo.update(
                user
            )

            # =====================================================
            # EVENT
            # =====================================================

            self.event_service.log(
                type=EventType.USER_ARCHIVED,
                message="Utilisateur archivé",
                user_id=admin_id,
                event_metadata={
                    "email": user.email,
                    "role": user.role.value,
                },
            )

            # =====================================================
            # COMMIT
            # =====================================================

            self.uow.commit()

            logger.info(
                "Utilisateur archivé",
                extra={
                    "user_id": user.id,
                    "admin_id": admin_id,
                },
            )

            return ArchiveUserResult(
    user_id=user.id,
)

        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur archivage utilisateur",
                extra={
                    "user_id": user_id,
                },
            )

            raise