import logging

from modules.auth.domain.exceptions import (
    Forbidden,
)

from modules.applications.application.results.delete_application_result import (
    DeleteApplicationResult,
)

from modules.applications.domain.enums import (
    ApplicationStatus,
)

from modules.applications.domain.exceptions import (
    ApplicationCannotBeDeleted,
    ApplicationNotFound,
)
from modules.applications.application.dtos.application_id_dto import ApplicationIdDTO

from modules.notifications.domain.enums import (
    NotificationEntityType,
)


logger = logging.getLogger(__name__)


class DeleteApplicationUseCase:
    """
    Supprime définitivement un dossier uniquement lorsqu'il est encore
    à l'état brouillon et qu'il appartient à l'utilisateur connecté.

    Avant la suppression du dossier, les données associées ainsi que
    les documents stockés sur S3 sont également supprimés.
    """
    def __init__(
        self,
        application_repo,
        document_repo,
        trade_in_repo,
        financing_repo,
        application_option_repo,
        reservation_repo,
        event_repo,
        notification_repo,
        s3_service,
        uow,
    ):
        self.application_repo = application_repo
        self.document_repo = document_repo
        self.trade_in_repo = trade_in_repo
        self.financing_repo = financing_repo
        self.application_option_repo = application_option_repo
        self.reservation_repo = reservation_repo
        self.event_repo = event_repo
        self.notification_repo = notification_repo
        self.s3_service = s3_service
        self.uow = uow

    def execute(
        self,
        dto: ApplicationIdDTO,
        current_user,
    ):
        try:
            # =====================================================
            # GET APPLICATION
            # =====================================================

            application = self.application_repo.get_by_id(
                dto.application_id
            )

            if not application:
                raise ApplicationNotFound()

            # =====================================================
            # SECURITY CHECK
            # =====================================================

            if application.user_id != current_user.id:
                raise Forbidden()

            # =====================================================
            # BUSINESS RULE
            # ONLY DRAFT CAN BE DELETED
            # =====================================================

            if application.status != ApplicationStatus.DRAFT:
                raise ApplicationCannotBeDeleted()

            # =====================================================
            # GET DOCUMENTS BEFORE DELETE
            # Needed for S3 cleanup
            # =====================================================

            documents = self.document_repo.get_by_application(
                dto.application_id
            )

            # =====================================================
            # DELETE S3 FILES
            # =====================================================

            for document in documents:
                if document.s3_key:
                    self.s3_service.delete_file(
                        document.s3_key
                    )

            # =====================================================
            # DELETE CHILD ENTITIES
            # =====================================================

            self.document_repo.delete_by_application(
                dto.application_id
            )

            self.event_repo.delete_by_application(
                dto.application_id
            )

            self.notification_repo.delete_by_entity(
                NotificationEntityType.APPLICATION,
                dto.application_id,
            )

            self.trade_in_repo.delete_by_application(
                dto.application_id
            )

            self.financing_repo.delete_by_application(
                dto.application_id
            )

            self.application_option_repo.delete_by_application(
                dto.application_id
            )

            self.reservation_repo.delete_by_application(
                dto.application_id
            )

            # =====================================================
            # DELETE APPLICATION
            # =====================================================

            self.application_repo.delete(
                dto.application_id
            )

            # =====================================================
            # COMMIT
            # =====================================================

            self.uow.commit()

            logger.warning(
                "Suppression définitive application",
                extra={
                    "application_id": dto.application_id,
                    "user_id": current_user.id,
                },
            )

            return DeleteApplicationResult(
                application_id=dto.application_id,
            )

        except Exception:
            self.uow.rollback()

            logger.exception(
                "Erreur suppression définitive application",
                extra={
                    "application_id": dto.application_id,
                },
            )

            raise