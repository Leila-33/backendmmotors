import logging

from modules.applications.domain.enums import EventType
from modules.auth.application.results.admin.update_user_role_result import (
    UpdateUserRoleResult,
)
from modules.auth.domain.enums import UserRole
from modules.auth.domain.exceptions import (
    Forbidden,
    UserNotFound,
)
from modules.auth.application.dtos.admin.update_user_role_dto import (
    UpdateUserRoleDTO,
)
logger = logging.getLogger(__name__)


class UpdateUserRoleUseCase:

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
        dto: UpdateUserRoleDTO,
        current_admin,
    ) -> UpdateUserRoleResult:

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
            # PROTECTION ADMIN
            # =====================================================

            if user.role == UserRole.ADMIN:
                raise Forbidden(
                    "Impossible de modifier un administrateur"
                )

            # =====================================================
            # UPDATE ROLE
            # =====================================================

            old_role = user.role

            user.role = dto.role

            self.user_repo.update(user)

            # =====================================================
            # EVENT
            # =====================================================

            self.event_service.log(
                type=EventType.USER_ROLE_UPDATED,
                message="Rôle utilisateur modifié",
                user_id=current_admin.id,
                event_metadata={
                    "email": user.email,
                    "old_role": old_role.value,
                    "dto.role": user.role.value,
                },
            )

            # =====================================================
            # COMMIT
            # =====================================================

            self.uow.commit()

            logger.warning(
                "Rôle utilisateur modifié",
                extra={
                    "user_id": user.id,
                    "old_role": old_role.value,
                    "dto.role": user.role.value,
                    "admin_id": current_admin.id,
                },
            )

            # =====================================================
            # RESULT
            # =====================================================

            return UpdateUserRoleResult(
                id=user.id,
                role=user.role,
            )

        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur modification rôle",
                extra={
                    "user_id": user_id,
                    "admin_id": (
                        current_admin.id
                        if current_admin
                        else None
                    ),
                },
            )

            raise