from modules.applications.domain.enums import ApplicationStatus

class ValidateApplicationPolicy:

    @staticmethod
    def can_validate(application) -> bool:
        return (
            application.status
            == ApplicationStatus.PROCESSING
        )