from modules.auth.domain.exceptions import UserNotFound, CannotArchiveAdmin
from modules.auth.domain.enums import UserRole
from modules.auth.api.schemas import ArchiveUserResponse

class ArchiveUserUseCase:

    def __init__(
        self,
        user_repo,
        uow,
    ):
        self.user_repo = user_repo
        self.uow = uow


    def execute(
        self,
        user_id: str
    ):

        try:

            user = (
                self.user_repo
                .get_by_id(user_id)
            )

            if not user:
                raise UserNotFound()


            if user.role == UserRole.ADMIN:
                raise CannotArchiveAdmin()


            user.archive()


            self.user_repo.update(
                user
            )


            self.uow.commit()


            return ArchiveUserResponse(
    message="Utilisateur archivé"
)


        except Exception:

            self.uow.rollback()

            raise