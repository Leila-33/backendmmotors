from modules.applications.domain.enums import ApplicationStatus
from modules.payments.domain.enums import SubscriptionStatus
from modules.applications.domain.exceptions import ApplicationAlreadyCancelled, CannotCancelApplication

class CancelApplicationPolicy:

    @staticmethod
    def can_cancel(application) -> bool:

        if application.status == ApplicationStatus.CANCELLED:
            return False

        if application.status in (
            ApplicationStatus.PAID,
            ApplicationStatus.COMPLETED,
        ):
            return False

        contract = application.financing_contract

        if (
            contract
            and contract.subscription_status in (
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.COMPLETED,
            )
        ):
            return False

        return True

    @staticmethod
    def validate(application) -> None:

        if application.status == ApplicationStatus.CANCELLED:
            raise ApplicationAlreadyCancelled()

        if not CancelApplicationPolicy.can_cancel(application):
            raise CannotCancelApplication()