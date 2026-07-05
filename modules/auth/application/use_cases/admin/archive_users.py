from modules.core.exceptions import (
    InvalidUserIds,
    UserAlreadyArchived,
    CannotArchiveAdmin
)
from modules.core.enums import UserRole
from modules.auth.api.schemas import ArchiveUsersResponse

class ArchiveUsersUseCase:

    def __init__(self, user_repo):
        self.user_repo = user_repo

    def execute(self, ids: list[str]):

        # =====================
        # VALIDATION
        # =====================
        if not ids:
            raise InvalidUserIds()

        users = self.user_repo.find_by_ids(ids)

        if not users:
            raise InvalidUserIds()

        # =====================
        # BUSINESS RULE
        # =====================
        for u in users:
            if u.is_deleted:
                raise UserAlreadyArchived(
                    f"Utilisateur {u.id} déjà archivé"
                )
            if u.role == UserRole.ADMIN:
                raise CannotArchiveAdmin()

        # =====================
        # ARCHIVE (SOFT DELETE)
        # =====================
        self.user_repo.archive_many(ids)

        return ArchiveUsersResponse(
            archived_count=len(users),
            user_ids=ids,
            message="Utilisateurs archivés avec succès"
        )