from datetime import datetime
from modules.auth.domain.exceptions import UserNotFound, CannotArchiveAdmin
from modules.auth.domain.enums import UserRole
from datetime import timezone

class ArchiveUserUseCase:

    def __init__(self, user_repo):
        self.user_repo = user_repo

    def execute(self, user_id: str):

        # =====================
        # AUTH CHECK
        # =====================
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise UserNotFound()

        # =====================
        # BUSINESS RULE
        # =====================
        if user.role == UserRole.ADMIN:
            raise CannotArchiveAdmin()

        user.is_deleted = True
        user.deleted_at = datetime.now(timezone.utc)
        user.is_active = False

        self.user_repo.update(user)

        return {"message": "Utilisateur archivé"}