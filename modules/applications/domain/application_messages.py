from modules.applications.domain.enums import (
    ApplicationStatus,
    EventType,
)


APPLICATION_EVENT_MAP = {
    ApplicationStatus.PROCESSING:
            EventType.APPLICATION_PROCESSING,

    ApplicationStatus.APPROVED:
        EventType.APPLICATION_APPROVED,

    ApplicationStatus.REJECTED:
        EventType.APPLICATION_REJECTED,

    ApplicationStatus.SUBMITTED:
        EventType.APPLICATION_SUBMITTED,
}