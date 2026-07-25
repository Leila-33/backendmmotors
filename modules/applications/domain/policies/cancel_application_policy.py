from modules.applications.domain.enums import ApplicationStatus
from modules.payments.domain.enums import SubscriptionStatus
from modules.applications.domain.exceptions import ApplicationAlreadyCancelled, CannotCancelApplication

class CancelApplicationPolicy:

    @staticmethod
    def can_cancel(
        application,
        role: str
    ) -> bool:

        if application.status == ApplicationStatus.CANCELLED:
            return False

        contract = application.financing_contract

        if (
            contract
            and contract.subscription_status in [
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.COMPLETED
            ]
        ):
            return False

        if role != "admin":

            if application.status in [
                ApplicationStatus.PAID,
                ApplicationStatus.COMPLETED
            ]:
                return False

        return True
    

    @staticmethod
    def validate(
        application,
        role: str
    ):

        if application.status == ApplicationStatus.CANCELLED:
            raise ApplicationAlreadyCancelled()

        contract = application.financing_contract

        if (
            contract
            and contract.subscription_status in [
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.COMPLETED
            ]
        ):
            raise CannotCancelApplication()
        
        if (
            role != "admin"
            and application.status in [
                ApplicationStatus.PAID,
                ApplicationStatus.COMPLETED
            ]
        ):
            raise CannotCancelApplication()