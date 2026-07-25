from modules.auth.domain.exceptions import UserNotFound, Forbidden
from modules.auth.domain.enums import UserRole

class ToggleUserActiveUseCase:

    def __init__(self, user_repo):
        self.user_repo = user_repo

    def execute(self, user_id: str, is_active: bool):

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
            raise Forbidden("Impossible de modifier un admin")

        user.is_active = is_active

        self.user_repo.update(user)

        return {
            "id": user.id,
            "is_active": user.is_active
        }