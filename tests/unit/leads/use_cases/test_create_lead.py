from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from modules.applications.domain.enums import EventType
from modules.leads.application.dtos.create_lead_dto import CreateLeadDTO
from modules.leads.application.results.create_lead_result import CreateLeadResult
from modules.leads.application.use_cases.create_lead import CreateLeadUseCase
from modules.leads.domain.enums import LeadStatus
from modules.leads.domain.exceptions import ActiveLeadAlreadyExists


@pytest.fixture
def lead_repository():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(lead_repository, event_service, unit_of_work):
    return CreateLeadUseCase(
        lead_repository=lead_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


@pytest.fixture
def dto():
    return CreateLeadDTO(
        user_id="user-123",
        vehicle_id="vehicle-123",
        first_name="Jean",
        last_name="Dupont",
        email="jean.dupont@example.com",
        phone="0612345678",
        message="Je suis intéressé par ce véhicule.",
    )


def test_execute_creates_lead_successfully(
    use_case,
    lead_repository,
    event_service,
    unit_of_work,
    dto,
):
    lead_repository.find_active_by_user_or_email_and_vehicle.return_value = None

    with patch(
        "modules.leads.application.use_cases.create_lead.uuid.uuid4",
        return_value="lead-123",
    ):
        result = use_case.execute(dto)

    assert isinstance(result, CreateLeadResult)
    assert result.lead_id == "lead-123"
    assert result.status == LeadStatus.NEW.value
    assert result.message == "Lead créé avec succès"

    lead_repository.find_active_by_user_or_email_and_vehicle.assert_called_once_with(
        user_id=dto.user_id,
        email=dto.email,
        vehicle_id=dto.vehicle_id,
    )

    lead_repository.save.assert_called_once()

    lead = lead_repository.save.call_args.args[0]

    assert lead.id == "lead-123"
    assert lead.vehicle_id == dto.vehicle_id
    assert lead.user_id == dto.user_id
    assert lead.first_name == dto.first_name
    assert lead.last_name == dto.last_name
    assert lead.email == dto.email
    assert lead.phone == dto.phone
    assert lead.message == dto.message
    assert lead.status == LeadStatus.NEW
    assert lead.assigned_to is None
    assert lead.created_at is not None
    assert lead.created_at.tzinfo is not None

    event_service.log.assert_called_once_with(
        type=EventType.LEAD_CREATED,
        message="Nouveau lead créé",
        user_id=dto.user_id,
        lead_id="lead-123",
        vehicle_id=dto.vehicle_id,
        event_metadata={
            "lead_id": "lead-123",
            "email": dto.email,
            "status": LeadStatus.NEW.value,
        },
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


def test_execute_rejects_existing_active_lead(
    use_case,
    lead_repository,
    event_service,
    unit_of_work,
    dto,
):
    lead_repository.find_active_by_user_or_email_and_vehicle.return_value = (
        SimpleNamespace(id="existing-lead")
    )

    with pytest.raises(ActiveLeadAlreadyExists):
        use_case.execute(dto)

    lead_repository.find_active_by_user_or_email_and_vehicle.assert_called_once_with(
        user_id=dto.user_id,
        email=dto.email,
        vehicle_id=dto.vehicle_id,
    )

    lead_repository.save.assert_not_called()
    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()

    unit_of_work.rollback.assert_called_once()


def test_execute_rolls_back_when_save_fails(
    use_case,
    lead_repository,
    event_service,
    unit_of_work,
    dto,
):
    lead_repository.find_active_by_user_or_email_and_vehicle.return_value = None
    lead_repository.save.side_effect = RuntimeError("Database error")

    with pytest.raises(RuntimeError, match="Database error"):
        use_case.execute(dto)

    lead_repository.save.assert_called_once()
    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()

    unit_of_work.rollback.assert_called_once()


def test_execute_rolls_back_when_event_logging_fails(
    use_case,
    lead_repository,
    event_service,
    unit_of_work,
    dto,
):
    lead_repository.find_active_by_user_or_email_and_vehicle.return_value = None
    event_service.log.side_effect = RuntimeError("Event error")

    with patch(
        "modules.leads.application.use_cases.create_lead.uuid.uuid4",
        return_value="lead-123",
    ):
        with pytest.raises(RuntimeError, match="Event error"):
            use_case.execute(dto)

    lead_repository.save.assert_called_once()
    event_service.log.assert_called_once()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_execute_rolls_back_when_commit_fails(
    use_case,
    lead_repository,
    event_service,
    unit_of_work,
    dto,
):
    lead_repository.find_active_by_user_or_email_and_vehicle.return_value = None
    unit_of_work.commit.side_effect = RuntimeError("Commit error")

    with patch(
        "modules.leads.application.use_cases.create_lead.uuid.uuid4",
        return_value="lead-123",
    ):
        with pytest.raises(RuntimeError, match="Commit error"):
            use_case.execute(dto)

    lead_repository.save.assert_called_once()
    event_service.log.assert_called_once()
    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()
