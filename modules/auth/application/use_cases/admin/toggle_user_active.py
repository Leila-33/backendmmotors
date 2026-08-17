import logging

from modules.applications.domain.enums import EventType
from modules.auth.application.results.admin.toggle_user_active_result import (
    ToggleUserActiveResult,
)
from modules.auth.domain.enums import UserRole
from modules.auth.domain.exceptions import (
    Forbidden,
    UserNotFound,
)
from modules.auth.application.dtos.admin.toggle_user_active_dto import (
    ToggleUserActiveDTO,
)
logger = logging.getLogger(__name__)


class ToggleUserActiveUseCase:

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
        dto: ToggleUserActiveDTO,
        current_admin,
    ) -> ToggleUserActiveResult:

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
                    "Impossible de désactiver un administrateur"
                )

            # =====================================================
            # UPDATE STATUS
            # =====================================================

            old_status = user.is_active

            user.is_active = dto.is_active

            self.user_repo.update(user)

            # =====================================================
            # EVENT
            # =====================================================

            if dto.is_active:
                event_type = EventType.USER_ACTIVATED
                message = "Utilisateur activé"
            else:
                event_type = EventType.USER_DEACTIVATED
                message = "Utilisateur désactivé"

            self.event_service.log(
                type=event_type,
                message=message,
                user_id=current_admin.id,
                event_metadata={
                    "email": user.email,
                    "old_status": old_status,
                    "new_status": user.is_active,
                },
            )

            # =====================================================
            # COMMIT
            # =====================================================

            self.uow.commit()

            logger.info(
                "Statut utilisateur modifié",
                extra={
                    "user_id": user.id,
                    "old_status": old_status,
                    "new_status": user.is_active,
                    "admin_id": current_admin.id,
                },
            )

            # =====================================================
            # RESULT
            # =====================================================

            return ToggleUserActiveResult(
                id=user.id,
                is_active=user.is_active,
            )

        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur activation compte",
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