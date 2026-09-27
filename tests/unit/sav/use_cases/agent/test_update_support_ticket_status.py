import pytest
from unittest.mock import AsyncMock, Mock
from types import SimpleNamespace

from modules.sav.application.dtos.agent.update_support_ticket_status_dto import (
    UpdateSupportTicketStatusDTO,
)
from modules.sav.application.results.agent.update_support_ticket_status_result import (
    UpdateSupportTicketStatusResult,
)
from modules.sav.application.use_cases.agent.update_support_ticket_status import (
    UpdateSupportTicketStatusUseCase,
)
from modules.sav.domain.exceptions import (
    SupportTicketNotFound,
)
from modules.sav.domain.enums import (
    TicketStatus,
)
from modules.applications.domain.enums import (
    EventType,
)


# ============================================================
# HELPERS
# ============================================================


def make_ticket(
    *,
    ticket_id="ticket-1",
    application_id="application-1",
    user_id="user-1",
    assigned_to="agent-1",
    status=None,
):
    if status is None:
        status = next(iter(TicketStatus))

    return SimpleNamespace(
        id=ticket_id,
        application_id=application_id,
        user_id=user_id,
        assigned_to=assigned_to,
        status=status,
    )


def make_dto(
    *,
    ticket_id="ticket-1",
    user_id="agent-1",
    status=None,
):
    if status is None:
        statuses = list(TicketStatus)

        if len(statuses) < 2:
            status = statuses[0]
        else:
            status = statuses[1]

    return SimpleNamespace(
        ticket_id=ticket_id,
        user_id=user_id,
        status=status,
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def repo():
    return Mock()


@pytest.fixture
def chat_manager():
    manager = Mock()
    manager.broadcast = AsyncMock()
    return manager


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    repo,
    chat_manager,
    event_service,
    unit_of_work,
):
    return UpdateSupportTicketStatusUseCase(
        repo=repo,
        chat_manager=chat_manager,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


@pytest.fixture
def ticket():
    return make_ticket()


# ============================================================
# TICKET NOT FOUND
# ============================================================


@pytest.mark.asyncio
async def test_ticket_not_found(
    use_case,
    repo,
    unit_of_work,
):
    dto = make_dto()

    repo.get_by_id.return_value = None

    with pytest.raises(
        SupportTicketNotFound
    ):
        await use_case.execute(dto)

    repo.get_by_id.assert_called_once_with(
        "ticket-1"
    )

    repo.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# NO CHANGE
# ============================================================


@pytest.mark.asyncio
async def test_same_status_returns_without_update(
    use_case,
    repo,
    event_service,
    chat_manager,
    unit_of_work,
    ticket,
):
    dto = make_dto(
        ticket_id="ticket-1",
        status=ticket.status,
    )

    repo.get_by_id.return_value = ticket

    result = await use_case.execute(dto)

    assert isinstance(
        result,
        UpdateSupportTicketStatusResult,
    )

    assert result.ticket is ticket

    repo.update.assert_not_called()

    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_not_called()

    chat_manager.broadcast.assert_not_awaited()


# ============================================================
# STATUS UPDATE
# ============================================================


@pytest.mark.asyncio
async def test_ticket_status_is_updated(
    use_case,
    repo,
    unit_of_work,
    ticket,
):
    statuses = list(TicketStatus)

    if len(statuses) < 2:
        pytest.skip(
            "TicketStatus doit contenir au moins deux statuts."
        )

    old_status = statuses[0]
    new_status = statuses[1]

    ticket.status = old_status

    dto = make_dto(
        ticket_id="ticket-1",
        status=new_status,
    )

    repo.get_by_id.return_value = ticket
    repo.update.return_value = ticket

    result = await use_case.execute(dto)

    assert ticket.status == new_status

    repo.update.assert_called_once_with(
        ticket
    )

    assert result.ticket is ticket

    unit_of_work.commit.assert_called_once()


# ============================================================
# REPOSITORY UPDATE
# ============================================================


@pytest.mark.asyncio
async def test_updated_ticket_returned_by_repository_is_used(
    use_case,
    repo,
    event_service,
    unit_of_work,
    ticket,
):
    statuses = list(TicketStatus)

    if len(statuses) < 2:
        pytest.skip(
            "TicketStatus doit contenir au moins deux statuts."
        )

    old_status = statuses[0]
    new_status = statuses[1]

    ticket.status = old_status

    dto = make_dto(
        ticket_id="ticket-1",
        status=new_status,
    )

    updated_ticket = make_ticket(
        ticket_id="ticket-1",
        application_id="application-42",
        user_id="user-42",
        assigned_to="agent-42",
        status=new_status,
    )

    repo.get_by_id.return_value = ticket
    repo.update.return_value = updated_ticket

    result = await use_case.execute(dto)

    assert result.ticket is updated_ticket

    event_service.log.assert_called_once()

    event_kwargs = event_service.log.call_args.kwargs

    assert event_kwargs["application_id"] == (
        "application-42"
    )

    assert event_kwargs["event_metadata"]["ticket_id"] == (
        "ticket-1"
    )

    assert event_kwargs["event_metadata"]["ticket_owner"] == (
        "user-42"
    )

    assert event_kwargs["event_metadata"]["assigned_to"] == (
        "agent-42"
    )


# ============================================================
# EVENT
# ============================================================


@pytest.mark.asyncio
async def test_status_changed_event_is_logged(
    use_case,
    repo,
    event_service,
    unit_of_work,
    ticket,
):
    statuses = list(TicketStatus)

    if len(statuses) < 2:
        pytest.skip(
            "TicketStatus doit contenir au moins deux statuts."
        )

    old_status = statuses[0]
    new_status = statuses[1]

    ticket.status = old_status

    dto = make_dto(
        ticket_id="ticket-1",
        user_id="agent-42",
        status=new_status,
    )

    repo.get_by_id.return_value = ticket
    repo.update.return_value = ticket

    await use_case.execute(dto)

    event_service.log.assert_called_once_with(
        type=EventType.SUPPORT_TICKET_STATUS_CHANGED,
        message="Statut du ticket SAV modifié",
        application_id="application-1",
        user_id="agent-42",
        event_metadata={
            "ticket_id": "ticket-1",
            "old_status": old_status.value,
            "new_status": new_status.value,
            "ticket_owner": "user-1",
            "assigned_to": "agent-1",
        },
    )

    unit_of_work.commit.assert_called_once()


# ============================================================
# COMMIT
# ============================================================


@pytest.mark.asyncio
async def test_commit_is_called(
    use_case,
    repo,
    unit_of_work,
    ticket,
):
    statuses = list(TicketStatus)

    if len(statuses) < 2:
        pytest.skip(
            "TicketStatus doit contenir au moins deux statuts."
        )

    ticket.status = statuses[0]

    dto = make_dto(
        status=statuses[1]
    )

    repo.get_by_id.return_value = ticket
    repo.update.return_value = ticket

    await use_case.execute(dto)

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# WEBSOCKET
# ============================================================


@pytest.mark.asyncio
async def test_websocket_broadcast_is_sent(
    use_case,
    repo,
    chat_manager,
    unit_of_work,
    ticket,
):
    statuses = list(TicketStatus)

    if len(statuses) < 2:
        pytest.skip(
            "TicketStatus doit contenir au moins deux statuts."
        )

    old_status = statuses[0]
    new_status = statuses[1]

    ticket.status = old_status

    dto = make_dto(
        ticket_id="ticket-1",
        status=new_status,
    )

    repo.get_by_id.return_value = ticket
    repo.update.return_value = ticket

    await use_case.execute(dto)

    chat_manager.broadcast.assert_awaited_once_with(
        ticket_id="ticket-1",
        payload={
            "type": "STATUS_UPDATED",
            "data": {
                "ticket_id": "ticket-1",
                "old_status": old_status.value,
                "status": new_status.value,
            },
        },
    )

    unit_of_work.commit.assert_called_once()


# ============================================================
# WEBSOCKET AFTER COMMIT
# ============================================================


@pytest.mark.asyncio
async def test_websocket_is_called_after_commit(
    use_case,
    repo,
    chat_manager,
    unit_of_work,
    ticket,
):
    statuses = list(TicketStatus)

    if len(statuses) < 2:
        pytest.skip(
            "TicketStatus doit contenir au moins deux statuts."
        )

    ticket.status = statuses[0]

    dto = make_dto(
        status=statuses[1]
    )

    repo.get_by_id.return_value = ticket
    repo.update.return_value = ticket

    call_order = []

    unit_of_work.commit.side_effect = (
        lambda: call_order.append("commit")
    )

    async def broadcast(*args, **kwargs):
        call_order.append("broadcast")

    chat_manager.broadcast.side_effect = broadcast

    await use_case.execute(dto)

    assert call_order == [
        "commit",
        "broadcast",
    ]


# ============================================================
# ROLLBACK — REPOSITORY GET
# ============================================================


@pytest.mark.asyncio
async def test_get_ticket_error_rolls_back(
    use_case,
    repo,
    unit_of_work,
):
    dto = make_dto()

    repo.get_by_id.side_effect = RuntimeError(
        "repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="repository error",
    ):
        await use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# ROLLBACK — REPOSITORY UPDATE
# ============================================================


@pytest.mark.asyncio
async def test_update_error_rolls_back(
    use_case,
    repo,
    unit_of_work,
    ticket,
):
    statuses = list(TicketStatus)

    if len(statuses) < 2:
        pytest.skip(
            "TicketStatus doit contenir au moins deux statuts."
        )

    ticket.status = statuses[0]

    dto = make_dto(
        status=statuses[1]
    )

    repo.get_by_id.return_value = ticket

    repo.update.side_effect = RuntimeError(
        "update error"
    )

    with pytest.raises(
        RuntimeError,
        match="update error",
    ):
        await use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# ROLLBACK — EVENT
# ============================================================


@pytest.mark.asyncio
async def test_event_error_rolls_back(
    use_case,
    repo,
    event_service,
    unit_of_work,
    ticket,
):
    statuses = list(TicketStatus)

    if len(statuses) < 2:
        pytest.skip(
            "TicketStatus doit contenir au moins deux statuts."
        )

    ticket.status = statuses[0]

    dto = make_dto(
        status=statuses[1]
    )

    repo.get_by_id.return_value = ticket
    repo.update.return_value = ticket

    event_service.log.side_effect = RuntimeError(
        "event error"
    )

    with pytest.raises(
        RuntimeError,
        match="event error",
    ):
        await use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# ROLLBACK — COMMIT
# ============================================================


@pytest.mark.asyncio
async def test_commit_error_rolls_back(
    use_case,
    repo,
    unit_of_work,
    ticket,
):
    statuses = list(TicketStatus)

    if len(statuses) < 2:
        pytest.skip(
            "TicketStatus doit contenir au moins deux statuts."
        )

    ticket.status = statuses[0]

    dto = make_dto(
        status=statuses[1]
    )

    repo.get_by_id.return_value = ticket
    repo.update.return_value = ticket

    unit_of_work.commit.side_effect = RuntimeError(
        "commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="commit error",
    ):
        await use_case.execute(dto)

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# ROLLBACK — WEBSOCKET
# ============================================================


@pytest.mark.asyncio
async def test_websocket_error_rolls_back(
    use_case,
    repo,
    chat_manager,
    unit_of_work,
    ticket,
):
    statuses = list(TicketStatus)

    if len(statuses) < 2:
        pytest.skip(
            "TicketStatus doit contenir au moins deux statuts."
        )

    ticket.status = statuses[0]

    dto = make_dto(
        status=statuses[1]
    )

    repo.get_by_id.return_value = ticket
    repo.update.return_value = ticket

    chat_manager.broadcast.side_effect = RuntimeError(
        "websocket error"
    )

    with pytest.raises(
        RuntimeError,
        match="websocket error",
    ):
        await use_case.execute(dto)

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# RESULT
# ============================================================


@pytest.mark.asyncio
async def test_result_is_returned(
    use_case,
    repo,
    unit_of_work,
    ticket,
):
    statuses = list(TicketStatus)

    if len(statuses) < 2:
        pytest.skip(
            "TicketStatus doit contenir au moins deux statuts."
        )

    old_status = statuses[0]
    new_status = statuses[1]

    ticket.status = old_status

    dto = make_dto(
        ticket_id="ticket-1",
        status=new_status,
    )

    repo.get_by_id.return_value = ticket
    repo.update.return_value = ticket

    result = await use_case.execute(dto)

    assert isinstance(
        result,
        UpdateSupportTicketStatusResult,
    )

    assert result.ticket is ticket


# ============================================================
# COMPLETE FLOW
# ============================================================


@pytest.mark.asyncio
async def test_update_support_ticket_status_complete_flow(
    use_case,
    repo,
    event_service,
    chat_manager,
    unit_of_work,
):
    statuses = list(TicketStatus)

    if len(statuses) < 2:
        pytest.skip(
            "TicketStatus doit contenir au moins deux statuts."
        )

    old_status = statuses[0]
    new_status = statuses[1]

    ticket = make_ticket(
        ticket_id="ticket-42",
        application_id="application-42",
        user_id="customer-42",
        assigned_to="agent-42",
        status=old_status,
    )

    dto = make_dto(
        ticket_id="ticket-42",
        user_id="agent-42",
        status=new_status,
    )

    repo.get_by_id.return_value = ticket
    repo.update.return_value = ticket

    result = await use_case.execute(dto)

    # Ticket récupéré
    repo.get_by_id.assert_called_once_with(
        "ticket-42"
    )

    # Statut modifié
    assert ticket.status == new_status

    # Repository
    repo.update.assert_called_once_with(
        ticket
    )

    # Event
    event_service.log.assert_called_once_with(
        type=EventType.SUPPORT_TICKET_STATUS_CHANGED,
        message="Statut du ticket SAV modifié",
        application_id="application-42",
        user_id="agent-42",
        event_metadata={
            "ticket_id": "ticket-42",
            "old_status": old_status.value,
            "new_status": new_status.value,
            "ticket_owner": "customer-42",
            "assigned_to": "agent-42",
        },
    )

    # Transaction
    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()

    # WebSocket
    chat_manager.broadcast.assert_awaited_once_with(
        ticket_id="ticket-42",
        payload={
            "type": "STATUS_UPDATED",
            "data": {
                "ticket_id": "ticket-42",
                "old_status": old_status.value,
                "status": new_status.value,
            },
        },
    )

    # Result
    assert isinstance(
        result,
        UpdateSupportTicketStatusResult,
    )

    assert result.ticket is ticket