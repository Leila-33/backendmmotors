from modules.payments.domain.enums import SubscriptionStatus


class SubscriptionStatusMapper:

    @staticmethod
    def from_stripe(status: str) -> SubscriptionStatus:

        mapping = {
            "active": SubscriptionStatus.ACTIVE,
            "trialing": SubscriptionStatus.ACTIVE,
            "past_due": SubscriptionStatus.PAST_DUE,
            "incomplete": SubscriptionStatus.PAST_DUE,
            "canceled": SubscriptionStatus.CANCELLED,
            "incomplete_expired": SubscriptionStatus.CANCELLED,
        }

        return mapping.get(
            status,
            SubscriptionStatus.ACTIVE
        )