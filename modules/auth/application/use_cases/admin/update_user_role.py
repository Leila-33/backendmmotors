from modules.auth.domain.exceptions import Forbidden, UserNotFound, InvalidUserRole
from modules.auth.domain.enums import UserRole
from modules.auth.api.schemas import UpdateUserRoleResponse
from modules.applications.domain.enums import EventType
import logging

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
        new_role: UserRole,
        current_admin
    ) -> UpdateUserRoleResponse:


        try:

            # =====================
            # GET USER
            # =====================

            user = (
                self.user_repo
                .get_by_id(user_id)
            )


            if not user:
                raise UserNotFound()



            # =====================
            # PROTECTION ADMIN
            # =====================

            if user.role == UserRole.ADMIN:

                raise Forbidden(
                    "Impossible de modifier un administrateur"
                )



            # =====================
            # VALIDATE ROLE
            # =====================

            if new_role not in UserRole:

                raise InvalidUserRole()



            # =====================
            # UPDATE ROLE
            # =====================
            old_role = user.role

            user.role = new_role


            self.user_repo.update(
                user
            )

            self.event_service.log(
    type=EventType.USER_ROLE_UPDATED,
    message="Rôle utilisateur modifié",
    user_id=current_admin,
    event_metadata={
        "email": user.email,
        "old_role": old_role.value,
        "new_role": user.role.value
    }
)

            self.uow.commit()

            logger.warning(
    "Rôle utilisateur modifié",
    extra={
        "user_id": user.id,
        "old_role": old_role.value,
        "new_role": user.role.value,
        "admin_id": current_admin.id,
    }
)

            return UpdateUserRoleResponse(

                id=user.id,

                role=user.role,

                message=(
                    "Rôle mis à jour"
                )
            )



        except Exception:

            self.uow.rollback()

            logger.exception(
    "Erreur modification role",
    extra={
        "user_id": user_id
    }
)
            raise