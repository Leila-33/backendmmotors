from modules.auth.domain.enums import UserRole
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.applications.application.dtos.application_id_dto import ApplicationIdDTO
from modules.applications.application.results.get_application_result import GetApplicationResult

class GetApplicationUseCase:

    def __init__(
        self,
        application_repository,
        payment_repository,
    ):
        self.application_repository = (
            application_repository
        )

        self.payment_repository = (
            payment_repository
        )

    def execute(
        self,
        dto: ApplicationIdDTO,
        current_user,
    ):

        # =========================
        # APPLICATION
        # =========================

        application = (
            self.application_repository
            .get_full_by_id(
                dto.application_id
            )
        )

        if application is None:
            raise ApplicationNotFound()

        # =========================
        # AUTORISATION
        # =========================

        if (
            current_user.role != UserRole.ADMIN
            and application.user_id != current_user.id
        ):
            raise ApplicationNotFound()

        # =========================
        # PAIEMENT
        # =========================

        payment = (
            self.payment_repository
            .get_latest_by_application_id(
                application.id
            )
        )

        payment_status = (
            payment.status.value
            if payment
            else None
        )

        # =========================
        # RÉSULTAT
        # =========================

        return GetApplicationResult(
            application=application,
            payment_status=payment_status,
        )