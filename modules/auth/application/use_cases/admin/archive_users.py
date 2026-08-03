from modules.auth.domain.exceptions import (
    InvalidUserIds,
    UserAlreadyArchived,
    CannotArchiveAdmin
)
from modules.auth.domain.enums import UserRole
from modules.auth.api.schemas import ArchiveUsersResponse
from datetime import datetime, timezone

class ArchiveUsersUseCase:

    def __init__(
        self,
        user_repo,
        uow,
    ):
        self.user_repo = user_repo
        self.uow = uow


    def execute(
        self,
        ids: list[str]
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



            # =====================
            # COMMIT
            # =====================

            self.uow.commit()



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

            raise