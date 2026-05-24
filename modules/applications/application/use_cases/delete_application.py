from modules.core.exceptions import ApplicationNotFound, Forbidden

class DeleteApplicationUseCase:

    def __init__(
        self,
        application_repo,
        document_repo,
        trade_in_repo,
        financing_repo,
        application_option_repo,
        event_repo,
        notification_repo,
        s3_service
    ):

        self.application_repo = application_repo
        self.document_repo = document_repo
        self.trade_in_repo = trade_in_repo
        self.financing_repo = financing_repo
        self.application_option_repo = application_option_repo
        self.event_repo = event_repo
        self.notification_repo = notification_repo
        self.s3_service = s3_service

    def execute(self, application_id: str, current_user):

        application = self.application_repo.get_by_id(application_id)

        if not application:
            raise ApplicationNotFound()

        # =========================
        # SECURITY CHECK
        # =========================
        if application.user_id != current_user.id:
            raise Forbidden()

        # =========================
        # 1. DELETE S3 DOCUMENTS
        # =========================
        documents = self.document_repo.get_by_application(application_id)

        for doc in documents:
            if doc.s3_key:
                self.s3_service.delete_file(doc.s3_key)

        # =========================
        # 2. DELETE DB CHILDREN
        # =========================
        self.document_repo.delete_by_application(application_id)

        self.event_repo.delete_by_application(application_id)

        self.notification_repo.delete_by_application(application_id)

        self.trade_in_repo.delete_by_application(application_id)

        self.financing_repo.delete_by_application(application_id)

        self.application_option_repo.delete_by_application(application_id)

        # =========================
        # 3. DELETE APPLICATION
        # =========================
        self.application_repo.delete(application_id)

        return {"success": True}