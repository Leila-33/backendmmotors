from modules.auth.domain.exceptions import (
    InvalidUserIds,
    UserAlreadyArchived,
    CannotArchiveAdmin
)
from modules.auth.domain.enums import UserRole
from modules.auth.api.schemas import ArchiveUsersResponse
from datetime import datetime, timezone
from modules.applications.domain.enums import EventType
import logging

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
        ids: list[str],
        current_admin
    ) -> ArchiveUsersResponse:

        try:

            # =====================
            # VALIDATION
            # =====================

            if not ids:
                raise InvalidUserIds()


            users = (
                self.user_repo
                .find_by_ids(ids)
            )


            if len(users) != len(ids):
                raise InvalidUserIds(
                    "Certains utilisateurs sont introuvables"
                )



            # =====================
            # BUSINESS RULE
            # =====================

            for user in users:

                if user.is_deleted:
                    raise UserAlreadyArchived(
                        f"Utilisateur {user.id} déjà archivé"
                    )


                if user.role == UserRole.ADMIN:
                    raise CannotArchiveAdmin()



            # =====================
            # ARCHIVE
            # =====================

            now = datetime.now(
                timezone.utc
            )


            for user in users:

                user.is_deleted = True

                user.is_active = False

                user.deleted_at = now


                self.user_repo.update(
                    user
                )
            
            self.event_service.log(
    type=EventType.ADMIN_ACTION,
    message="Archivage de plusieurs utilisateurs",
    event_metadata={
        "action": "archive_users",
        "user_ids": ids,
        "count": len(ids)
    }
)


            self.uow.commit()

            logger.info(
    "Archivage utilisateurs en masse effectué",
    extra={
        "count": len(users),
        "admin_id": current_admin.id,
    }
)


            return ArchiveUsersResponse(

                archived_count=len(users),

                user_ids=[
                    user.id
                    for user in users
                ],

                message=(
                    "Utilisateurs archivés avec succès"
                )
            )


        except Exception:

            self.uow.rollback()

            logger.exception(
    "Erreur archivage utilisateurs en masse"
)
            raise