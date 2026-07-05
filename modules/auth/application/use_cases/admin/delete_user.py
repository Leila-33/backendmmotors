from modules.core.exceptions import UserNotFound, Forbidden
from modules.auth.domain.repositories.user_repository import UserRepository
from datetime import datetime, timezone
from modules.core.enums import UserRole

class DeleteUserUseCase:

    def __init__(self, repo: UserRepository):
        self.repo = repo

    def execute(self, user_id: str):

        # 2. get user
        user = self.repo.get_by_id(user_id)

        if not user:
            raise UserNotFound()

        # 3. protection super admin
        if user.role == UserRole.ADMIN:
            raise Forbidden()

        # 4. soft delete (recommandé)
        user.is_deleted = True
        user.deleted_at = datetime.now(timezone.utc)

        self.repo.update(user)

        return {"message": "Utilisateur supprimé"}