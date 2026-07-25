from enum import Enum

class NotificationType(str, Enum):
    APPLICATION_APPROVED = "application_approved"

    APPLICATION_REJECTED = "application_rejected"

    APPLICATION_SUBMITTED = "application_submitted"

    DOCUMENT_REJECTED = "document_rejected"
    TEST_DRIVE_CONFIRMED = "test_drive_confirmed"

    TEST_DRIVE_CANCELLED = "test_drive_cancelled"

    TEST_DRIVE_REJECTED = "test_drive_rejected"

    TEST_DRIVE_COMPLETED = "test_drive_completed"
    QUOTE_SENT = "quote_sent"
    QUOTE_ACCEPTED = "quote_accepted"
    QUOTE_REFUSED = "quote_refused"

class NotificationStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"

class NotificationEntityType(str, Enum):
    QUOTE = "quote"
    APPLICATION = "application"
    DOCUMENT = "document"
    TEST_DRIVE = "test_drive"