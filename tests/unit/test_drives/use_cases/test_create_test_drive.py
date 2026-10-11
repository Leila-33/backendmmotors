from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call

import pytest

from modules.test_drives.application.use_cases.create_test_drive import (
    CreateTestDriveUseCase,
)
from modules.test_drives.domain.enums import TestDriveStatus
from modules.test_drives.domain.exceptions import (
    TestDriveAlreadyExists,
    TestDrivePastDate,
    TestDriveSlotUnavailable,
)
from modules.vehicles.domain.enums import VehicleStatus
from modules.vehicles.domain.exceptions import (
    VehicleNotFound,
    VehicleNotAvailableForTestDrive,
)
from modules.notifications.domain.enums import (
    NotificationEntityType,
    NotificationType,
)
from modules.applications.domain.enums import EventType
from modules.auth.domain.enums import UserRole


class TestCreateTestDriveUseCase:

    @pytest.fixture
    def user_repository(self):
        return MagicMock()

    @pytest.fixture
    def test_drive_repository(self):
        return MagicMock()

    @pytest.fixture
    def vehicle_repository(self):
        return MagicMock()

    @pytest.fixture
    def event_service(self):
        return MagicMock()

    @pytest.fixture
    def notification_service(self):
        service = MagicMock()
        service.send = AsyncMock()
        service.send_update = AsyncMock()
        return service

    @pytest.fixture
    def unit_of_work(self):
        return MagicMock()

    @pytest.fixture
    def use_case(
        self,
        user_repository,
        test_drive_repository,
        vehicle_repository,
        event_service,
        notification_service,
        unit_of_work,
    ):
        return CreateTestDriveUseCase(
            user_repository=user_repository,
            test_drive_repository=test_drive_repository,
            vehicle_repository=vehicle_repository,
            event_service=event_service,
            notification_service=notification_service,
            unit_of_work=unit_of_work,
        )

    @staticmethod
    def create_vehicle(
        vehicle_id=1,
        status=VehicleStatus.PUBLISHED,
    ):
        return SimpleNamespace(
            id=vehicle_id,
            status=status,
        )

    @staticmethod
    def create_dto(
        vehicle_id=1,
        appointment_date=None,
        comment="Essai routier",
    ):
        if appointment_date is None:
            appointment_date = (
                datetime.now(timezone.utc) + timedelta(days=2)
            )

        return SimpleNamespace(
            vehicle_id=vehicle_id,
            appointment_date=appointment_date,
            comment=comment,
        )

    @staticmethod
    def create_admin(admin_id=100):
        return SimpleNamespace(id=admin_id)

    def configure_success(
        self,
        vehicle_repository,
        test_drive_repository,
        user_repository,
        admins=None,
    ):
        vehicle_repository.get_by_id.return_value = (
            self.create_vehicle()
        )

        test_drive_repository.has_existing_blocking_test_drive.return_value = (
            False
        )
        test_drive_repository.find_conflicting_slot.return_value = None
        test_drive_repository.count_pending.return_value = 1

        user_repository.get_by_role.return_value = (
            admins if admins is not None else []
        )

    # ==========================================================
    # SUCCESS
    # ==========================================================

    @pytest.mark.asyncio
    async def test_creates_test_drive_successfully(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
        event_service,
        unit_of_work,
    ):
        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
        )

        dto = self.create_dto()
        user_id = "customer-1"

        result = await use_case.execute(dto, user_id)

        assert result.user_id == user_id
        assert result.vehicle_id == dto.vehicle_id
        assert result.appointment_date == dto.appointment_date
        assert result.status == TestDriveStatus.PENDING
        assert result.comment == dto.comment
        assert result.created_at.tzinfo is not None

        test_drive_repository.create.assert_called_once()
        unit_of_work.commit.assert_called_once()
        unit_of_work.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_creates_test_drive_with_generated_id(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
    ):
        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
        )

        result = await use_case.execute(
            self.create_dto(),
            "customer-1",
        )

        assert isinstance(result.id, str)
        assert len(result.id) == 36

    @pytest.mark.asyncio
    async def test_creates_test_drive_with_pending_status(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
    ):
        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
        )

        result = await use_case.execute(
            self.create_dto(),
            "customer-1",
        )

        assert result.status == TestDriveStatus.PENDING

    @pytest.mark.asyncio
    async def test_passes_created_entity_to_repository(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
    ):
        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
        )

        dto = self.create_dto()
        user_id = "customer-1"

        result = await use_case.execute(dto, user_id)

        test_drive_repository.create.assert_called_once_with(result)

    # ==========================================================
    # VEHICLE VALIDATION
    # ==========================================================

    @pytest.mark.asyncio
    async def test_raises_when_vehicle_does_not_exist(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
        event_service,
        unit_of_work,
    ):
        vehicle_repository.get_by_id.return_value = None
        dto = self.create_dto()

        with pytest.raises(VehicleNotFound):
            await use_case.execute(dto, "customer-1")

        vehicle_repository.get_by_id.assert_called_once_with(
            dto.vehicle_id
        )
        test_drive_repository.create.assert_not_called()
        event_service.log.assert_not_called()
        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "status",
        [
            status
            for status in VehicleStatus
            if status != VehicleStatus.PUBLISHED
        ],
    )
    async def test_rejects_vehicle_not_published(
        self,
        status,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
        unit_of_work,
    ):
        vehicle_repository.get_by_id.return_value = (
            self.create_vehicle(status=status)
        )

        with pytest.raises(VehicleNotAvailableForTestDrive):
            await use_case.execute(
                self.create_dto(),
                "customer-1",
            )

        test_drive_repository.has_existing_blocking_test_drive.assert_not_called()
        test_drive_repository.create.assert_not_called()
        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    # ==========================================================
    # EXISTING REQUEST
    # ==========================================================

    @pytest.mark.asyncio
    async def test_checks_existing_blocking_request(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
    ):
        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
        )

        dto = self.create_dto(vehicle_id=42)

        await use_case.execute(dto, "customer-1")

        test_drive_repository.has_existing_blocking_test_drive.assert_called_once_with(
            user_id="customer-1",
            vehicle_id=42,
        )

    @pytest.mark.asyncio
    async def test_rejects_when_blocking_request_already_exists(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
        unit_of_work,
    ):
        vehicle_repository.get_by_id.return_value = (
            self.create_vehicle()
        )
        test_drive_repository.has_existing_blocking_test_drive.return_value = (
            True
        )

        with pytest.raises(TestDriveAlreadyExists):
            await use_case.execute(
                self.create_dto(),
                "customer-1",
            )

        test_drive_repository.find_conflicting_slot.assert_not_called()
        test_drive_repository.create.assert_not_called()
        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    # ==========================================================
    # APPOINTMENT DATE
    # ==========================================================

    @pytest.mark.asyncio
    async def test_rejects_naive_appointment_datetime(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
        unit_of_work,
    ):
        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
        )

        naive_date = datetime.now() + timedelta(days=2)
        dto = self.create_dto(appointment_date=naive_date)

        with pytest.raises(
            ValueError,
            match="La date du rendez-vous doit inclure un fuseau horaire",
        ):
            await use_case.execute(dto, "customer-1")

        test_drive_repository.find_conflicting_slot.assert_not_called()
        test_drive_repository.create.assert_not_called()
        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_rejects_past_appointment_date(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
        unit_of_work,
    ):
        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
        )

        past_date = datetime.now(timezone.utc) - timedelta(days=1)

        with pytest.raises(TestDrivePastDate):
            await use_case.execute(
                self.create_dto(appointment_date=past_date),
                "customer-1",
            )

        test_drive_repository.find_conflicting_slot.assert_not_called()
        test_drive_repository.create.assert_not_called()
        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_rejects_appointment_at_current_time(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
        unit_of_work,
    ):
        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
        )

        current_date = datetime.now(timezone.utc) - timedelta(seconds=1)

        with pytest.raises(TestDrivePastDate):
            await use_case.execute(
                self.create_dto(appointment_date=current_date),
                "customer-1",
            )

        test_drive_repository.create.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    # ==========================================================
    # SLOT AVAILABILITY
    # ==========================================================

    @pytest.mark.asyncio
    async def test_checks_conflicting_slot(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
    ):
        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
        )

        dto = self.create_dto(vehicle_id=42)

        await use_case.execute(dto, "customer-1")

        test_drive_repository.find_conflicting_slot.assert_called_once_with(
            vehicle_id=42,
            appointment_date=dto.appointment_date,
        )

    @pytest.mark.asyncio
    async def test_rejects_unavailable_slot(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
        unit_of_work,
    ):
        vehicle_repository.get_by_id.return_value = (
            self.create_vehicle()
        )
        test_drive_repository.has_existing_blocking_test_drive.return_value = (
            False
        )
        test_drive_repository.find_conflicting_slot.return_value = (
            MagicMock()
        )

        with pytest.raises(TestDriveSlotUnavailable):
            await use_case.execute(
                self.create_dto(),
                "customer-1",
            )

        test_drive_repository.create.assert_not_called()
        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    # ==========================================================
    # EVENT
    # ==========================================================

    @pytest.mark.asyncio
    async def test_logs_test_drive_created_event(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
        event_service,
    ):
        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
        )

        result = await use_case.execute(
            self.create_dto(),
            "customer-1",
        )

        event_service.log.assert_called_once_with(
            type=EventType.TEST_DRIVE_CREATED,
            message="Demande d'essai véhicule créée",
            user_id="customer-1",
            vehicle_id=result.vehicle_id,
            test_drive_id=result.id,
            event_metadata={
                "appointment_date": result.appointment_date.isoformat(),
                "status": result.status.value,
            },
        )

    # ==========================================================
    # ADMIN NOTIFICATIONS
    # ==========================================================

    @pytest.mark.asyncio
    async def test_loads_administrators(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
    ):
        admins = [
            self.create_admin(1),
            self.create_admin(2),
        ]

        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
            admins=admins,
        )

        await use_case.execute(
            self.create_dto(),
            "customer-1",
        )

        user_repository.get_by_role.assert_called_once_with(
            UserRole.ADMIN
        )

    @pytest.mark.asyncio
    async def test_notifies_each_administrator(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
        notification_service,
    ):
        admins = [
            self.create_admin(1),
            self.create_admin(2),
        ]

        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
            admins=admins,
        )

        result = await use_case.execute(
            self.create_dto(),
            "customer-1",
        )

        assert notification_service.send.await_count == 2

        notification_service.send.assert_has_awaits(
            [
                call(
                    user_id="1",
                    title="Nouvel essai routier",
                    message="Un client a demandé un essai routier.",
                    notif_type=NotificationType.TEST_DRIVE_CREATED,
                    entity_type=NotificationEntityType.TEST_DRIVE,
                    entity_id=result.id,
                ),
                call(
                    user_id="2",
                    title="Nouvel essai routier",
                    message="Un client a demandé un essai routier.",
                    notif_type=NotificationType.TEST_DRIVE_CREATED,
                    entity_type=NotificationEntityType.TEST_DRIVE,
                    entity_id=result.id,
                ),
            ]
        )

    @pytest.mark.asyncio
    async def test_continues_if_admin_notification_fails(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
        notification_service,
        unit_of_work,
    ):
        admins = [
            self.create_admin(1),
            self.create_admin(2),
        ]

        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
            admins=admins,
        )

        notification_service.send.side_effect = [
            Exception("Notification failed"),
            None,
        ]

        result = await use_case.execute(
            self.create_dto(),
            "customer-1",
        )

        assert result is not None
        assert notification_service.send.await_count == 2
        unit_of_work.commit.assert_called_once()
        unit_of_work.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_creates_test_drive_when_there_are_no_admins(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
        notification_service,
        unit_of_work,
    ):
        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
            admins=[],
        )

        result = await use_case.execute(
            self.create_dto(),
            "customer-1",
        )

        assert result is not None
        notification_service.send.assert_not_awaited()
        notification_service.send_update.assert_not_awaited()
        unit_of_work.commit.assert_called_once()

    # ==========================================================
    # COMMIT / ROLLBACK
    # ==========================================================

    @pytest.mark.asyncio
    async def test_commits_successful_creation(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
        unit_of_work,
    ):
        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
        )

        await use_case.execute(
            self.create_dto(),
            "customer-1",
        )

        unit_of_work.commit.assert_called_once()
        unit_of_work.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_rolls_back_when_creation_fails(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
        unit_of_work,
    ):
        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
        )

        test_drive_repository.create.side_effect = Exception(
            "Creation failed"
        )

        with pytest.raises(Exception, match="Creation failed"):
            await use_case.execute(
                self.create_dto(),
                "customer-1",
            )

        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_rolls_back_when_event_logging_fails(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
        event_service,
        unit_of_work,
    ):
        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
        )

        event_service.log.side_effect = Exception("Event failed")

        with pytest.raises(Exception, match="Event failed"):
            await use_case.execute(
                self.create_dto(),
                "customer-1",
            )

        test_drive_repository.create.assert_called_once()
        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_rolls_back_when_commit_fails(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
        unit_of_work,
    ):
        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
        )

        unit_of_work.commit.side_effect = Exception("Commit failed")

        with pytest.raises(Exception, match="Commit failed"):
            await use_case.execute(
                self.create_dto(),
                "customer-1",
            )

        unit_of_work.commit.assert_called_once()
        unit_of_work.rollback.assert_called_once()

    # ==========================================================
    # POST-COMMIT PENDING COUNT
    # ==========================================================

    @pytest.mark.asyncio
    async def test_counts_pending_test_drives_after_commit(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
        unit_of_work,
    ):
        admins = [self.create_admin(1)]

        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
            admins=admins,
        )

        await use_case.execute(
            self.create_dto(),
            "customer-1",
        )

        test_drive_repository.count_pending.assert_called_once()

        unit_of_work.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcasts_pending_count_to_each_admin(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
        notification_service,
    ):
        admins = [
            self.create_admin(1),
            self.create_admin(2),
        ]

        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
            admins=admins,
        )

        test_drive_repository.count_pending.return_value = 8

        await use_case.execute(
            self.create_dto(),
            "customer-1",
        )

        notification_service.send_update.assert_has_awaits(
            [
                call(
                    user_id="1",
                    payload={
                        "type": "TEST_DRIVE_PENDING_UPDATED",
                        "count": 8,
                    },
                ),
                call(
                    user_id="2",
                    payload={
                        "type": "TEST_DRIVE_PENDING_UPDATED",
                        "count": 8,
                    },
                ),
            ]
        )

    @pytest.mark.asyncio
    async def test_returns_created_test_drive_if_pending_count_fails(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
        unit_of_work,
    ):
        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
        )

        test_drive_repository.count_pending.side_effect = Exception(
            "Count failed"
        )

        result = await use_case.execute(
            self.create_dto(),
            "customer-1",
        )

        assert result is not None
        unit_of_work.commit.assert_called_once()
        unit_of_work.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_does_not_rollback_if_pending_broadcast_fails(
        self,
        use_case,
        vehicle_repository,
        test_drive_repository,
        user_repository,
        notification_service,
        unit_of_work,
    ):
        admins = [self.create_admin(1)]

        self.configure_success(
            vehicle_repository,
            test_drive_repository,
            user_repository,
            admins=admins,
        )

        notification_service.send_update.side_effect = Exception(
            "Broadcast failed"
        )

        result = await use_case.execute(
            self.create_dto(),
            "customer-1",
        )

        assert result is not None
        unit_of_work.commit.assert_called_once()
        unit_of_work.rollback.assert_not_called()