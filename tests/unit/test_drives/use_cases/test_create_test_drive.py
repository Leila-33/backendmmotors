from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest

from modules.applications.domain.enums import EventType
from modules.test_drives.application.dtos.create_test_drive_dto import (
    CreateTestDriveDTO,
)
from modules.test_drives.application.use_cases.create_test_drive import (
    CreateTestDriveUseCase,
)
from modules.test_drives.domain.entities.test_drive import TestDrive
from modules.test_drives.domain.enums import TestDriveStatus
from modules.test_drives.domain.exceptions import (
    TestDrivePastDate,
    TestDriveSlotUnavailable,
)
from modules.vehicles.domain.enums import VehicleStatus
from modules.vehicles.domain.exceptions import (
    VehicleNotAvailableForTestDrive,
    VehicleNotFound,
)


# ============================================================
# HELPERS
# ============================================================


def make_dto(
    *,
    vehicle_id: str = "vehicle-1",
    appointment_date: datetime | None = None,
    comment: str | None = "Je souhaite essayer ce véhicule.",
):
    if appointment_date is None:
        appointment_date = datetime.now(
            timezone.utc
        ) + timedelta(days=1)

    return CreateTestDriveDTO(
        vehicle_id=vehicle_id,
        appointment_date=appointment_date,
        comment=comment,
    )


def make_vehicle(
    *,
    vehicle_id: str = "vehicle-1",
    status: VehicleStatus = VehicleStatus.PUBLISHED,
):
    vehicle = Mock()

    vehicle.id = vehicle_id
    vehicle.status = status

    return vehicle


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def test_drive_repository():
    return Mock()


@pytest.fixture
def vehicle_repository():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    test_drive_repository,
    vehicle_repository,
    event_service,
    unit_of_work,
):
    return CreateTestDriveUseCase(
        test_drive_repository=test_drive_repository,
        vehicle_repository=vehicle_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


@pytest.fixture
def dto():
    return make_dto()


@pytest.fixture
def user_id():
    return "user-1"


@pytest.fixture
def vehicle():
    return make_vehicle()


# ============================================================
# VEHICLE
# ============================================================


def test_vehicle_not_found(
    use_case,
    vehicle_repository,
    test_drive_repository,
    event_service,
    unit_of_work,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = None

    with pytest.raises(
        VehicleNotFound
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    vehicle_repository.get_by_id.assert_called_once_with(
        dto.vehicle_id
    )

    test_drive_repository.find_conflicting_slot.assert_not_called()
    test_drive_repository.create.assert_not_called()

    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


@pytest.mark.parametrize(
    "status",
    [
        status
        for status in VehicleStatus
        if status != VehicleStatus.PUBLISHED
    ],
)
def test_vehicle_not_published_cannot_be_used_for_test_drive(
    status,
    use_case,
    vehicle_repository,
    test_drive_repository,
    event_service,
    unit_of_work,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle(
        status=status
    )

    with pytest.raises(
        VehicleNotAvailableForTestDrive
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    vehicle_repository.get_by_id.assert_called_once_with(
        dto.vehicle_id
    )

    test_drive_repository.find_conflicting_slot.assert_not_called()
    test_drive_repository.create.assert_not_called()

    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_published_vehicle_can_be_used_for_test_drive(
    use_case,
    vehicle_repository,
    test_drive_repository,
    dto,
    user_id,
    vehicle,
):
    vehicle_repository.get_by_id.return_value = vehicle
    test_drive_repository.find_conflicting_slot.return_value = None

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    assert isinstance(
        result,
        TestDrive,
    )


# ============================================================
# DATE
# ============================================================


def test_past_appointment_date_is_rejected(
    use_case,
    vehicle_repository,
    test_drive_repository,
    event_service,
    unit_of_work,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    dto = make_dto(
        appointment_date=datetime.now(
            timezone.utc
        ) - timedelta(minutes=1)
    )

    with pytest.raises(
        TestDrivePastDate
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    test_drive_repository.find_conflicting_slot.assert_not_called()
    test_drive_repository.create.assert_not_called()

    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_current_appointment_date_is_rejected(
    use_case,
    vehicle_repository,
    test_drive_repository,
    event_service,
    unit_of_work,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    appointment_date = datetime.now(
        timezone.utc
    )

    dto = make_dto(
        appointment_date=appointment_date
    )

    with pytest.raises(
        TestDrivePastDate
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    test_drive_repository.find_conflicting_slot.assert_not_called()
    test_drive_repository.create.assert_not_called()

    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_future_appointment_date_is_accepted(
    use_case,
    vehicle_repository,
    test_drive_repository,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()
    test_drive_repository.find_conflicting_slot.return_value = None

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    assert isinstance(
        result,
        TestDrive,
    )


# ============================================================
# SLOT
# ============================================================


def test_conflicting_slot_is_rejected(
    use_case,
    vehicle_repository,
    test_drive_repository,
    event_service,
    unit_of_work,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    test_drive_repository.find_conflicting_slot.return_value = Mock()

    with pytest.raises(
        TestDriveSlotUnavailable
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    test_drive_repository.find_conflicting_slot.assert_called_once_with(
        vehicle_id=dto.vehicle_id,
        appointment_date=dto.appointment_date,
    )

    test_drive_repository.create.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_available_slot_allows_creation(
    use_case,
    vehicle_repository,
    test_drive_repository,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    test_drive_repository.find_conflicting_slot.return_value = None

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    assert isinstance(
        result,
        TestDrive,
    )

    test_drive_repository.find_conflicting_slot.assert_called_once_with(
        vehicle_id=dto.vehicle_id,
        appointment_date=dto.appointment_date,
    )


# ============================================================
# CREATION
# ============================================================


def test_test_drive_is_created(
    use_case,
    vehicle_repository,
    test_drive_repository,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()
    test_drive_repository.find_conflicting_slot.return_value = None

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    test_drive_repository.create.assert_called_once()

    created_test_drive = (
        test_drive_repository.create.call_args.args[0]
    )

    assert created_test_drive is result


def test_created_test_drive_contains_correct_user(
    use_case,
    vehicle_repository,
    test_drive_repository,
    dto,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()
    test_drive_repository.find_conflicting_slot.return_value = None

    result = use_case.execute(
        dto=dto,
        user_id="user-42",
    )

    assert result.user_id == "user-42"


def test_created_test_drive_contains_correct_vehicle(
    use_case,
    vehicle_repository,
    test_drive_repository,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()
    test_drive_repository.find_conflicting_slot.return_value = None

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    assert result.vehicle_id == dto.vehicle_id


def test_created_test_drive_contains_appointment_date(
    use_case,
    vehicle_repository,
    test_drive_repository,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()
    test_drive_repository.find_conflicting_slot.return_value = None

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    assert result.appointment_date == (
        dto.appointment_date
    )


def test_created_test_drive_contains_comment(
    use_case,
    vehicle_repository,
    test_drive_repository,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()
    test_drive_repository.find_conflicting_slot.return_value = None

    dto = make_dto(
        comment="Je souhaite essayer le véhicule."
    )

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    assert result.comment == (
        "Je souhaite essayer le véhicule."
    )


@pytest.mark.parametrize(
    "comment",
    [
        None,
        "",
        "Commentaire",
    ],
)
def test_created_test_drive_preserves_comment(
    comment,
    use_case,
    vehicle_repository,
    test_drive_repository,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()
    test_drive_repository.find_conflicting_slot.return_value = None

    dto = make_dto(
        comment=comment
    )

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    assert result.comment == comment


def test_created_test_drive_has_pending_status(
    use_case,
    vehicle_repository,
    test_drive_repository,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()
    test_drive_repository.find_conflicting_slot.return_value = None

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    assert result.status == TestDriveStatus.PENDING


def test_created_test_drive_has_uuid_id(
    use_case,
    vehicle_repository,
    test_drive_repository,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()
    test_drive_repository.find_conflicting_slot.return_value = None

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    assert result.id is not None
    assert isinstance(
        result.id,
        str,
    )

    # UUID valide
    assert len(result.id) == 36
    assert result.id.count("-") == 4


def test_created_test_drive_id_comes_from_uuid4(
    use_case,
    vehicle_repository,
    test_drive_repository,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()
    test_drive_repository.find_conflicting_slot.return_value = None

    fixed_uuid = "12345678-1234-5678-1234-567812345678"

    with patch(
        "modules.test_drives.application.use_cases.create_test_drive.uuid4",
        return_value=fixed_uuid,
    ):
        result = use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    assert result.id == fixed_uuid


def test_created_test_drive_created_at_is_utc_aware(
    use_case,
    vehicle_repository,
    test_drive_repository,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()
    test_drive_repository.find_conflicting_slot.return_value = None

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    assert result.created_at is not None
    assert result.created_at.tzinfo is not None
    assert result.created_at.utcoffset().total_seconds() == 0


# ============================================================
# EVENT
# ============================================================


def test_event_is_logged(
    use_case,
    vehicle_repository,
    test_drive_repository,
    event_service,
    dto,
    user_id,
):
    vehicle = make_vehicle()

    vehicle_repository.get_by_id.return_value = vehicle
    test_drive_repository.find_conflicting_slot.return_value = None

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    event_service.log.assert_called_once()

    kwargs = event_service.log.call_args.kwargs

    assert kwargs["type"] == EventType.TEST_DRIVE_CREATED
    assert kwargs["message"] == (
        "Demande d'essai véhicule créée"
    )

    assert kwargs["user_id"] == user_id
    assert kwargs["vehicle_id"] == vehicle.id
    assert kwargs["test_drive_id"] == result.id


def test_event_contains_correct_metadata(
    use_case,
    vehicle_repository,
    test_drive_repository,
    event_service,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()
    test_drive_repository.find_conflicting_slot.return_value = None

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    kwargs = event_service.log.call_args.kwargs

    metadata = kwargs["event_metadata"]

    assert metadata["appointment_date"] == (
        dto.appointment_date.isoformat()
    )

    assert metadata["status"] == (
        TestDriveStatus.PENDING.value
    )

    assert metadata == {
        "appointment_date": dto.appointment_date.isoformat(),
        "status": TestDriveStatus.PENDING.value,
    }


# ============================================================
# COMMIT
# ============================================================


def test_unit_of_work_is_committed(
    use_case,
    vehicle_repository,
    test_drive_repository,
    unit_of_work,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()
    test_drive_repository.find_conflicting_slot.return_value = None

    use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


def test_commit_happens_after_event(
    use_case,
    vehicle_repository,
    test_drive_repository,
    event_service,
    unit_of_work,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()
    test_drive_repository.find_conflicting_slot.return_value = None

    call_order = []

    event_service.log.side_effect = (
        lambda **kwargs: call_order.append(
            "event"
        )
    )

    unit_of_work.commit.side_effect = (
        lambda: call_order.append(
            "commit"
        )
    )

    use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    assert call_order == [
        "event",
        "commit",
    ]


# ============================================================
# REPOSITORY ERRORS
# ============================================================


def test_vehicle_repository_error_rolls_back(
    use_case,
    vehicle_repository,
    unit_of_work,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.side_effect = RuntimeError(
        "vehicle repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="vehicle repository error",
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_slot_repository_error_rolls_back(
    use_case,
    vehicle_repository,
    test_drive_repository,
    unit_of_work,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    test_drive_repository.find_conflicting_slot.side_effect = (
        RuntimeError(
            "slot repository error"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="slot repository error",
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_create_repository_error_rolls_back(
    use_case,
    vehicle_repository,
    test_drive_repository,
    unit_of_work,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()
    test_drive_repository.find_conflicting_slot.return_value = None

    test_drive_repository.create.side_effect = (
        RuntimeError(
            "create error"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="create error",
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_event_service_error_rolls_back(
    use_case,
    vehicle_repository,
    test_drive_repository,
    event_service,
    unit_of_work,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()
    test_drive_repository.find_conflicting_slot.return_value = None

    event_service.log.side_effect = RuntimeError(
        "event error"
    )

    with pytest.raises(
        RuntimeError,
        match="event error",
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_commit_error_rolls_back(
    use_case,
    vehicle_repository,
    test_drive_repository,
    unit_of_work,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()
    test_drive_repository.find_conflicting_slot.return_value = None

    unit_of_work.commit.side_effect = RuntimeError(
        "commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="commit error",
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# ROLLBACK ON BUSINESS EXCEPTIONS
# ============================================================


@pytest.mark.parametrize(
    "exception",
    [
        VehicleNotFound,
        VehicleNotAvailableForTestDrive,
        TestDrivePastDate,
        TestDriveSlotUnavailable,
    ],
)
def test_business_error_always_rolls_back(
    exception,
    use_case,
    vehicle_repository,
    test_drive_repository,
    unit_of_work,
    dto,
    user_id,
):
    if exception is VehicleNotFound:
        vehicle_repository.get_by_id.return_value = None

    elif exception is VehicleNotAvailableForTestDrive:
        vehicle_repository.get_by_id.return_value = make_vehicle(
            status=next(
                status
                for status in VehicleStatus
                if status != VehicleStatus.PUBLISHED
            )
        )

    elif exception is TestDrivePastDate:
        vehicle_repository.get_by_id.return_value = make_vehicle()

        dto = make_dto(
            appointment_date=datetime.now(
                timezone.utc
            ) - timedelta(days=1)
        )

    elif exception is TestDriveSlotUnavailable:
        vehicle_repository.get_by_id.return_value = make_vehicle()
        test_drive_repository.find_conflicting_slot.return_value = (
            Mock()
        )

    with pytest.raises(exception):
        use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# NO UNEXPECTED OPERATIONS
# ============================================================


def test_success_does_not_call_rollback(
    use_case,
    vehicle_repository,
    test_drive_repository,
    unit_of_work,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()
    test_drive_repository.find_conflicting_slot.return_value = None

    use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    unit_of_work.rollback.assert_not_called()


def test_vehicle_not_found_does_not_create_test_drive(
    use_case,
    vehicle_repository,
    test_drive_repository,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = None

    with pytest.raises(
        VehicleNotFound
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    test_drive_repository.create.assert_not_called()


def test_slot_conflict_does_not_create_test_drive(
    use_case,
    vehicle_repository,
    test_drive_repository,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()
    test_drive_repository.find_conflicting_slot.return_value = Mock()

    with pytest.raises(
        TestDriveSlotUnavailable
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    test_drive_repository.create.assert_not_called()


def test_success_calls_expected_repositories_only(
    use_case,
    vehicle_repository,
    test_drive_repository,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()
    test_drive_repository.find_conflicting_slot.return_value = None

    use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    vehicle_repository.get_by_id.assert_called_once_with(
        dto.vehicle_id
    )

    test_drive_repository.find_conflicting_slot.assert_called_once_with(
        vehicle_id=dto.vehicle_id,
        appointment_date=dto.appointment_date,
    )

    test_drive_repository.create.assert_called_once()