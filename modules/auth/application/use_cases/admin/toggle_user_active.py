from modules.auth.domain.exceptions import UserNotFound, Forbidden
from modules.auth.domain.enums import UserRole
from modules.auth.api.schemas import ToggleUserActiveResponse

class ToggleUserActiveUseCase:


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
        is_active: bool,
    ) -> ToggleUserActiveResponse:


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
                    "Impossible de désactiver un administrateur"
                )



            # =====================
            # UPDATE STATUS
            # =====================

            user.is_active = is_active


            self.user_repo.update(
                user
            )



            # =====================
            # COMMIT
            # =====================

            self.uow.commit()



            return ToggleUserActiveResponse(

                id=user.id,

                is_active=user.is_active,

                message=(
                    "Statut utilisateur mis à jour"
                )
            )



        except Exception:

            self.uow.rollback()

            raise