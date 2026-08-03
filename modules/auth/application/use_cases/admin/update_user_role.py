from modules.auth.domain.exceptions import Forbidden, UserNotFound, InvalidUserRole
from modules.auth.domain.enums import UserRole
from modules.auth.api.schemas import UpdateUserRoleResponse

class UpdateUserRoleUseCase:


    def __init__(
        self,
        user_repo,
        uow,
    ):

        self.user_repo = user_repo

        self.uow = uow



    def execute(
        self,
        user_id: str,
        new_role: UserRole,
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

            user.role = new_role


            self.user_repo.update(
                user
            )



            # =====================
            # COMMIT
            # =====================

            self.uow.commit()



            return UpdateUserRoleResponse(

                id=user.id,

                role=user.role,

                message=(
                    "Rôle mis à jour"
                )
            )



        except Exception:

            self.uow.rollback()

            raise