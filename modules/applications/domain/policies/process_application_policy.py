from modules.applications.domain.enums import ApplicationStatus

class ProcessApplicationPolicy:

    @staticmethod
    def can_process(application) -> bool:
        return (
            application.status
            == ApplicationStatus.SUBMITTED
        )