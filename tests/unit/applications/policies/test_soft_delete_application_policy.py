import pytest

from modules.applications.domain.entities.application import Application
from modules.applications.domain.enums import ApplicationStatus
from modules.applications.domain.exceptions import (
    ApplicationAlreadyDeleted,
    CannotDeleteApplication,
)
from modules.applications.domain.policies.soft_delete_application_policy import (
    SoftDeleteApplicationPolicy,
)


def make_application(
    *,
    status=ApplicationStatus.COMPLETED,
    deleted_at=None,
):
    return Application(
        id="application-1",
        user_id="user-1",
        vehicle_id="vehicle-1",
        status=status,
        deleted_at=deleted_at,
    )


def test_can_delete_returns_true_for_cancelled_application():
    application = make_application(
        status=ApplicationStatus.CANCELLED,
    )

    assert SoftDeleteApplicationPolicy.can_delete(
        application
    ) is True


def test_can_delete_returns_true_for_completed_application():
    application = make_application(
        status=ApplicationStatus.COMPLETED,
    )

    assert SoftDeleteApplicationPolicy.can_delete(
        application
    ) is True


def test_can_delete_returns_true_for_rejected_application():
    application = make_application(
        status=ApplicationStatus.REJECTED,
    )

    assert SoftDeleteApplicationPolicy.can_delete(
        application
    ) is True


def test_can_delete_returns_false_when_already_deleted():
    application = make_application(
        deleted_at="already-deleted",
    )

    assert SoftDeleteApplicationPolicy.can_delete(
        application
    ) is False


def test_can_delete_returns_false_for_invalid_status():
    application = make_application(
        status=ApplicationStatus.DRAFT,
    )

    assert SoftDeleteApplicationPolicy.can_delete(
        application
    ) is False


def test_validate_raises_when_already_deleted():
    application = make_application(
        deleted_at="already-deleted",
    )

    with pytest.raises(ApplicationAlreadyDeleted):
        SoftDeleteApplicationPolicy.validate(
            application
        )


def test_validate_raises_for_invalid_status():
    application = make_application(
        status=ApplicationStatus.DRAFT,
    )

    with pytest.raises(CannotDeleteApplication):
        SoftDeleteApplicationPolicy.validate(
            application
        )