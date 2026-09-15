from modules.applications.domain.enums import ApplicationStatus

class RejectApplicationPolicy:

    @staticmethod
    def can_reject(application) -> bool:
        return (
            application.status
            == ApplicationStatus.PROCESSING
        )