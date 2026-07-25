from modules.auth.domain.exceptions import Forbidden, UserNotFound
from modules.auth.domain.enums import UserRole

class UpdateUserRoleUseCase:

    def __init__(self, user_repo):
        self.user_repo = user_repo

    def execute(self, user_id: str, new_role: str):

        # =====================
        # GET USER
        # =====================
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise UserNotFound()

        # =====================
        # PROTECTION ADMIN
        # =====================
        if user.role == UserRole.ADMIN:
            raise Forbidden("Impossible de modifier un admin")

        # =====================
        # UPDATE ROLE
        # =====================
        user.role = new_role

        self.user_repo.update(user)

        return {
            "id": user.id,
            "role": user.role,
            "message": "Rôle mis à jour"
        }