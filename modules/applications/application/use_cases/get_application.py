from modules.auth.domain.enums import UserRole
from modules.applications.domain.exceptions import ApplicationNotFound


class GetApplicationUseCase:

    def __init__(
        self,
        application_repository,
        payment_repository,
    ):
        self.application_repository = application_repository
        self.payment_repository = payment_repository


    def execute(
        self,
        application_id,
        current_user,
    ):

        application = (
            self.application_repository
            .get_full_by_id(application_id)
        )

        if not application:
            raise ApplicationNotFound()


        if (
            current_user.role != UserRole.ADMIN
            and application.user_id != current_user.id
        ):
            raise ApplicationNotFound()


        latest_payment = (
            self.payment_repository
            .get_latest_payment(application.id)
        )


        return application, latest_payment