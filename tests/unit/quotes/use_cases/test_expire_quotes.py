from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from modules.quotes.application.use_cases.expire_quotes import (
    ExpireQuotesUseCase,
)
from modules.applications.domain.enums import EventType


@pytest.fixture
def dependencies():
    return {
        "quote_repository": Mock(),
        "event_service": Mock(),
        "unit_of_work": Mock(),
    }


@pytest.fixture
def use_case(dependencies):
    return ExpireQuotesUseCase(
        quote_repository=dependencies["quote_repository"],
        event_service=dependencies["event_service"],
        unit_of_work=dependencies["unit_of_work"],
    )


def make_quote(
    quote_id="quote-123",
    old_status=None,
    new_status=None,
    expired_at=None,
):
    quote = Mock()

    quote.id = quote_id
    quote.status = old_status

    quote.lead = SimpleNamespace(
        vehicle=SimpleNamespace(
            id="vehicle-123",
        )
    )

    if new_status is not None:
        quote.expire.side_effect = (
            lambda: setattr(
                quote,
                "status",
                new_status,
            )
        )

    quote.expired_at = expired_at

    return quote


# ============================================================
# SUCCESS — AUCUN DEVIS
# ============================================================

def test_execute_with_no_quotes_to_expire(
    use_case,
    dependencies,
):
    dependencies[
        "quote_repository"
    ].find_quotes_to_expire.return_value = []

    use_case.execute()

    dependencies[
        "quote_repository"
    ].find_quotes_to_expire.assert_called_once()

    dependencies[
        "event_service"
    ].log.assert_not_called()

    dependencies[
        "quote_repository"
    ].update.assert_not_called()

    dependencies[
        "unit_of_work"
    ].commit.assert_called_once()

    dependencies[
        "unit_of_work"
    ].rollback.assert_not_called()


# ============================================================
# SUCCESS — UN DEVIs
# ============================================================

def test_execute_expires_one_quote(
    use_case,
    dependencies,
):
    old_status = SimpleNamespace(
        value="SENT"
    )

    new_status = SimpleNamespace(
        value="EXPIRED"
    )

    expired_at = SimpleNamespace(
        isoformat=Mock(
            return_value="2026-09-13T12:00:00+00:00"
        )
    )

    quote = make_quote(
        quote_id="quote-123",
        old_status=old_status,
        new_status=new_status,
        expired_at=expired_at,
    )

    dependencies[
        "quote_repository"
    ].find_quotes_to_expire.return_value = [
        quote
    ]

    use_case.execute()

    quote.expire.assert_called_once()

    dependencies[
        "quote_repository"
    ].update.assert_called_once_with(
        quote
    )

    dependencies[
        "event_service"
    ].log.assert_called_once_with(
        type=EventType.QUOTE_EXPIRED,
        message="Devis expiré automatiquement",
        quote_id="quote-123",
        vehicle_id="vehicle-123",
        user_id=None,
        event_metadata={
            "old_status": "SENT",
            "new_status": "EXPIRED",
            "expiration_date": (
                "2026-09-13T12:00:00+00:00"
            ),
        },
    )

    dependencies[
        "unit_of_work"
    ].commit.assert_called_once()

    dependencies[
        "unit_of_work"
    ].rollback.assert_not_called()


# ============================================================
# SUCCESS — PLUSIEURS DEVIS
# ============================================================

def test_execute_expires_multiple_quotes(
    use_case,
    dependencies,
):
    old_status_1 = SimpleNamespace(value="SENT")
    new_status_1 = SimpleNamespace(value="EXPIRED")

    old_status_2 = SimpleNamespace(value="SENT")
    new_status_2 = SimpleNamespace(value="EXPIRED")

    quote_1 = make_quote(
        quote_id="quote-1",
        old_status=old_status_1,
        new_status=new_status_1,
    )

    quote_2 = make_quote(
        quote_id="quote-2",
        old_status=old_status_2,
        new_status=new_status_2,
    )

    dependencies[
        "quote_repository"
    ].find_quotes_to_expire.return_value = [
        quote_1,
        quote_2,
    ]

    use_case.execute()

    quote_1.expire.assert_called_once()
    quote_2.expire.assert_called_once()

    assert (
        dependencies[
            "quote_repository"
        ].update.call_count
        == 2
    )

    assert (
        dependencies[
            "event_service"
        ].log.call_count
        == 2
    )

    first_event = (
        dependencies["event_service"]
        .log.call_args_list[0]
    )

    second_event = (
        dependencies["event_service"]
        .log.call_args_list[1]
    )

    assert first_event.kwargs["quote_id"] == "quote-1"
    assert second_event.kwargs["quote_id"] == "quote-2"

    dependencies[
        "unit_of_work"
    ].commit.assert_called_once()

    dependencies[
        "unit_of_work"
    ].rollback.assert_not_called()


# ============================================================
# EXPIRATION_DATE = None
# ============================================================

def test_execute_handles_missing_expiration_date(
    use_case,
    dependencies,
):
    old_status = SimpleNamespace(value="SENT")
    new_status = SimpleNamespace(value="EXPIRED")

    quote = make_quote(
        quote_id="quote-123",
        old_status=old_status,
        new_status=new_status,
        expired_at=None,
    )

    dependencies[
        "quote_repository"
    ].find_quotes_to_expire.return_value = [
        quote
    ]

    use_case.execute()

    dependencies[
        "event_service"
    ].log.assert_called_once_with(
        type=EventType.QUOTE_EXPIRED,
        message="Devis expiré automatiquement",
        quote_id="quote-123",
        vehicle_id="vehicle-123",
        user_id=None,
        event_metadata={
            "old_status": "SENT",
            "new_status": "EXPIRED",
            "expiration_date": None,
        },
    )

    dependencies[
        "unit_of_work"
    ].commit.assert_called_once()


# ============================================================
# REPOSITORY ERROR
# ============================================================

def test_execute_rollback_when_find_quotes_fails(
    use_case,
    dependencies,
):
    dependencies[
        "quote_repository"
    ].find_quotes_to_expire.side_effect = (
        RuntimeError("Database error")
    )

    with pytest.raises(RuntimeError):
        use_case.execute()

    dependencies[
        "unit_of_work"
    ].rollback.assert_called_once()

    dependencies[
        "unit_of_work"
    ].commit.assert_not_called()


# ============================================================
# UPDATE ERROR
# ============================================================

def test_execute_rollback_when_update_fails(
    use_case,
    dependencies,
):
    old_status = SimpleNamespace(value="SENT")
    new_status = SimpleNamespace(value="EXPIRED")

    quote = make_quote(
        quote_id="quote-123",
        old_status=old_status,
        new_status=new_status,
    )

    dependencies[
        "quote_repository"
    ].find_quotes_to_expire.return_value = [
        quote
    ]

    dependencies[
        "quote_repository"
    ].update.side_effect = (
        RuntimeError("Update error")
    )

    with pytest.raises(RuntimeError):
        use_case.execute()

    quote.expire.assert_called_once()

    dependencies[
        "quote_repository"
    ].update.assert_called_once_with(
        quote
    )

    dependencies[
        "event_service"
    ].log.assert_not_called()

    dependencies[
        "unit_of_work"
    ].rollback.assert_called_once()

    dependencies[
        "unit_of_work"
    ].commit.assert_not_called()


# ============================================================
# EVENT ERROR
# ============================================================

def test_execute_rollback_when_event_fails(
    use_case,
    dependencies,
):
    old_status = SimpleNamespace(value="SENT")
    new_status = SimpleNamespace(value="EXPIRED")

    quote = make_quote(
        quote_id="quote-123",
        old_status=old_status,
        new_status=new_status,
    )

    dependencies[
        "quote_repository"
    ].find_quotes_to_expire.return_value = [
        quote
    ]

    dependencies[
        "event_service"
    ].log.side_effect = (
        RuntimeError("Event error")
    )

    with pytest.raises(RuntimeError):
        use_case.execute()

    quote.expire.assert_called_once()

    dependencies[
        "quote_repository"
    ].update.assert_called_once_with(
        quote
    )

    dependencies[
        "event_service"
    ].log.assert_called_once()

    dependencies[
        "unit_of_work"
    ].rollback.assert_called_once()

    dependencies[
        "unit_of_work"
    ].commit.assert_not_called()


# ============================================================
# COMMIT ERROR
# ============================================================

def test_execute_rollback_when_commit_fails(
    use_case,
    dependencies,
):
    old_status = SimpleNamespace(value="SENT")
    new_status = SimpleNamespace(value="EXPIRED")

    quote = make_quote(
        quote_id="quote-123",
        old_status=old_status,
        new_status=new_status,
    )

    dependencies[
        "quote_repository"
    ].find_quotes_to_expire.return_value = [
        quote
    ]

    dependencies[
        "unit_of_work"
    ].commit.side_effect = (
        RuntimeError("Commit error")
    )

    with pytest.raises(RuntimeError):
        use_case.execute()

    quote.expire.assert_called_once()

    dependencies[
        "quote_repository"
    ].update.assert_called_once_with(
        quote
    )

    dependencies[
        "event_service"
    ].log.assert_called_once()

    dependencies[
        "unit_of_work"
    ].commit.assert_called_once()

    dependencies[
        "unit_of_work"
    ].rollback.assert_called_once()