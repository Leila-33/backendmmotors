from modules.auth.domain.exceptions import UserNotFound, CannotArchiveAdmin
from modules.auth.domain.enums import UserRole
from modules.auth.api.schemas import ArchiveUserResponse
from modules.applications.domain.enums import EventType

class ArchiveUserUseCase:

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
            self.event_service.log(
                type=EventType.USER_ARCHIVED,
                message="Utilisateur archivé",
                user_id=user.id,
                event_metadata={
                    "email": user.email,
                    "role": user.role.value
                }
            )

            self.uow.commit()


            return ArchiveUserResponse(
    message="Utilisateur archivé"
)


        except Exception:

            self.uow.rollback()

            raise