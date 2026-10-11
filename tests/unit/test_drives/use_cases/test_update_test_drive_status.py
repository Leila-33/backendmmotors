from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call

import pytest

from modules.test_drives.application.use_cases.update_test_drive_status import (
    UpdateTestDriveStatusUseCase,
)
from modules.test_drives.application.dtos.update_test_drive_status_dto import (
    UpdateTestDriveStatusDTO,
)
from modules.test_drives.domain.enums import TestDriveStatus
from modules.test_drives.domain.exceptions import (
    TestDriveNotFound,
    TestDriveStatusForbidden,
)
from modules.test_drives.domain.test_drive_messages import (
    TEST_DRIVE_EVENT_MAP,
    TEST_DRIVE_STATUS_LABELS,
)
from modules.auth.domain.enums import UserRole
from modules.auth.domain.exceptions import Forbidden
from modules.notifications.domain.enums import (
    NotificationEntityType,
    NotificationType,
)


class TestUpdateTestDriveStatusUseCase:

    @pytest.fixture
    def repository(self):
        return MagicMock()

    @pytest.fixture
    def user_repository(self):
        return MagicMock()

    @pytest.fixture
    def event_service(self):
        return MagicMock()

    @pytest.fixture
    def unit_of_work(self):
        return MagicMock()

    @pytest.fixture
    def notification_service(self):
        service = MagicMock()
        service.send = AsyncMock()
        service.send_update = AsyncMock()
        return service

    @pytest.fixture
    def use_case(
        self,
        repository,
        user_repository,
        event_service,
        unit_of_work,
        notification_service,
    ):
        return UpdateTestDriveStatusUseCase(
            repository=repository,
            user_repository=user_repository,
            event_service=event_service,
            unit_of_work=unit_of_work,
            notification_service=notification_service,
        )

    @staticmethod
    def create_test_drive(
        test_drive_id="td-1",
        user_id="client-1",
        vehicle_id=10,
        status=TestDriveStatus.PENDING,
        with_user=True,
        with_vehicle=True,
    ):
        user = (
            SimpleNamespace(
                id=user_id,
                email="client@example.com",
            )
            if with_user
            else None
        )

        vehicle = (
            SimpleNamespace(
                id=vehicle_id,
                brand="Toyota",
                model="Corolla",
            )
            if with_vehicle
            else None
        )

        return SimpleNamespace(
            id=test_drive_id,
            user_id=user_id,
            vehicle_id=vehicle_id,
            status=status,
            appointment_date=datetime(
                2027, 5, 20, 14, 30,
                tzinfo=timezone.utc,
            ),
            user=user,
            vehicle=vehicle,
        )

    @staticmethod
    def create_dto(
        test_drive_id="td-1",
        actor_id="admin-1",
        actor_role=UserRole.ADMIN,
        status=TestDriveStatus.CONFIRMED,
    ):
        return UpdateTestDriveStatusDTO(
            test_drive_id=test_drive_id,
            actor_id=actor_id,
            actor_role=actor_role,
            status=status,
        )

    def configure_success(
        self,
        repository,
        test_drive,
    ):
        repository.get_full_by_id.return_value = test_drive
        repository.update.side_effect = lambda entity: entity
        repository.count_pending.return_value = 3

    # ==========================================================
    # SUCCESS
    # ==========================================================

    @pytest.mark.asyncio
    async def test_updates_test_drive_status_successfully(
        self,
        use_case,
        repository,
        unit_of_work,
    ):
        test_drive = self.create_test_drive()
        self.configure_success(repository, test_drive)

        dto = self.create_dto(
            status=TestDriveStatus.CONFIRMED,
        )

        result = await use_case.execute(dto)

        assert result.status == TestDriveStatus.CONFIRMED
        repository.get_full_by_id.assert_called_once_with(
            dto.test_drive_id
        )
        repository.update.assert_called_once_with(test_drive)
        unit_of_work.commit.assert_called_once()
        unit_of_work.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_returns_updated_test_drive(
        self,
        use_case,
        repository,
    ):
        test_drive = self.create_test_drive()
        self.configure_success(repository, test_drive)

        result = await use_case.execute(
            self.create_dto(status=TestDriveStatus.CONFIRMED)
        )

        assert result is test_drive

    @pytest.mark.asyncio
    async def test_loads_test_drive_by_id(
        self,
        use_case,
        repository,
    ):
        test_drive = self.create_test_drive()
        self.configure_success(repository, test_drive)

        dto = self.create_dto(test_drive_id="td-42")

        await use_case.execute(dto)

        repository.get_full_by_id.assert_called_once_with("td-42")

    # ==========================================================
    # NOT FOUND
    # ==========================================================

    @pytest.mark.asyncio
    async def test_raises_when_test_drive_does_not_exist(
        self,
        use_case,
        repository,
        unit_of_work,
    ):
        repository.get_full_by_id.return_value = None

        with pytest.raises(TestDriveNotFound):
            await use_case.execute(self.create_dto())

        repository.update.assert_not_called()
        unit_of_work.commit.assert_not_called()

        # L'exception est levée avant le bloc try.
        unit_of_work.rollback.assert_not_called()

    # ==========================================================
    # CLIENT AUTHORIZATION
    # ==========================================================

    @pytest.mark.asyncio
    async def test_rejects_client_access_to_another_users_test_drive(
        self,
        use_case,
        repository,
        unit_of_work,
    ):
        test_drive = self.create_test_drive(
            user_id="client-1",
        )
        repository.get_full_by_id.return_value = test_drive

        dto = self.create_dto(
            actor_id="client-2",
            actor_role=UserRole.CLIENT,
            status=TestDriveStatus.CANCELLED,
        )

        with pytest.raises(Forbidden):
            await use_case.execute(dto)

        repository.update.assert_not_called()
        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_client_can_only_request_cancellation(
        self,
        use_case,
        repository,
        unit_of_work,
    ):
        test_drive = self.create_test_drive(
            user_id="client-1",
        )
        repository.get_full_by_id.return_value = test_drive

        dto = self.create_dto(
            actor_id="client-1",
            actor_role=UserRole.CLIENT,
            status=TestDriveStatus.CONFIRMED,
        )

        with pytest.raises(TestDriveStatusForbidden):
            await use_case.execute(dto)

        repository.update.assert_not_called()
        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_client_can_cancel_own_test_drive(
        self,
        use_case,
        repository,
        unit_of_work,
    ):
        test_drive = self.create_test_drive(
            user_id="client-1",
            status=TestDriveStatus.PENDING,
        )
        self.configure_success(repository, test_drive)

        dto = self.create_dto(
            actor_id="client-1",
            actor_role=UserRole.CLIENT,
            status=TestDriveStatus.CANCELLED,
        )

        result = await use_case.execute(dto)

        assert result.status == TestDriveStatus.CANCELLED
        repository.update.assert_called_once_with(test_drive)
        unit_of_work.commit.assert_called_once()

    # ==========================================================
    # NO CHANGE
    # ==========================================================

    @pytest.mark.asyncio
    async def test_returns_without_update_when_status_is_unchanged(
        self,
        use_case,
        repository,
        event_service,
        notification_service,
        unit_of_work,
    ):
        test_drive = self.create_test_drive(
            status=TestDriveStatus.CONFIRMED,
        )
        repository.get_full_by_id.return_value = test_drive

        result = await use_case.execute(
            self.create_dto(status=TestDriveStatus.CONFIRMED)
        )

        assert result is test_drive
        repository.update.assert_not_called()
        event_service.log.assert_not_called()
        notification_service.send.assert_not_awaited()
        notification_service.send_update.assert_not_awaited()
        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_not_called()

    # ==========================================================
    # EVENT
    # ==========================================================

    @pytest.mark.asyncio
    async def test_logs_event_for_status_with_event_mapping(
        self,
        use_case,
        repository,
        event_service,
    ):
        target_status = TestDriveStatus.CONFIRMED
        test_drive = self.create_test_drive()
        self.configure_success(repository, test_drive)

        dto = self.create_dto(status=target_status)

        await use_case.execute(dto)

        if target_status in TEST_DRIVE_EVENT_MAP:
            event_service.log.assert_called_once_with(
                test_drive_id=test_drive.id,
                type=TEST_DRIVE_EVENT_MAP[target_status],
                message=(
                    "Statut de l'essai routier changé vers "
                    f"{TEST_DRIVE_STATUS_LABELS[target_status]}"
                ),
                vehicle_id=test_drive.vehicle_id,
                user_id=dto.actor_id,
                event_metadata={
                    "customer_id": test_drive.user_id,
                    "old_status": TestDriveStatus.PENDING.value,
                    "new_status": target_status.value,
                },
            )
        else:
            event_service.log.assert_not_called()

    @pytest.mark.asyncio
    async def test_event_contains_old_and_new_status(
        self,
        use_case,
        repository,
        event_service,
    ):
        test_drive = self.create_test_drive(
            status=TestDriveStatus.PENDING,
        )
        self.configure_success(repository, test_drive)

        await use_case.execute(
            self.create_dto(status=TestDriveStatus.CONFIRMED)
        )

        if TestDriveStatus.CONFIRMED in TEST_DRIVE_EVENT_MAP:
            metadata = event_service.log.call_args.kwargs[
                "event_metadata"
            ]

            assert metadata["old_status"] == TestDriveStatus.PENDING.value
            assert metadata["new_status"] == TestDriveStatus.CONFIRMED.value
            assert metadata["customer_id"] == test_drive.user_id

    # ==========================================================
    # CUSTOMER NOTIFICATION
    # ==========================================================

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "status,expected_title,expected_type",
        [
            (
                TestDriveStatus.CONFIRMED,
                "Essai routier confirmé",
                NotificationType.TEST_DRIVE_CONFIRMED,
            ),
            (
                TestDriveStatus.REJECTED,
                "Essai routier refusé",
                NotificationType.TEST_DRIVE_REJECTED,
            ),
            (
                TestDriveStatus.CANCELLED,
                "Essai routier annulé",
                NotificationType.TEST_DRIVE_CANCELLED,
            ),
            (
                TestDriveStatus.COMPLETED,
                "Essai routier terminé",
                NotificationType.TEST_DRIVE_COMPLETED,
            ),
        ],
    )
    async def test_sends_notification_for_supported_status(
        self,
        status,
        expected_title,
        expected_type,
        use_case,
        repository,
        notification_service,
    ):
        test_drive = self.create_test_drive(
            status=TestDriveStatus.PENDING,
        )
        self.configure_success(repository, test_drive)

        await use_case.execute(
            self.create_dto(status=status)
        )

        notification_service.send.assert_awaited_once()

        kwargs = notification_service.send.call_args.kwargs

        assert kwargs["user_id"] == test_drive.user_id
        assert kwargs["email"] == test_drive.user.email
        assert kwargs["entity_type"] == NotificationEntityType.TEST_DRIVE
        assert kwargs["entity_id"] == test_drive.id
        assert kwargs["title"] == expected_title
        assert kwargs["notif_type"] == expected_type
        assert kwargs["message"]

    @pytest.mark.asyncio
    async def test_notification_contains_vehicle_name(
        self,
        use_case,
        repository,
        notification_service,
    ):
        test_drive = self.create_test_drive()
        self.configure_success(repository, test_drive)

        await use_case.execute(
            self.create_dto(status=TestDriveStatus.CONFIRMED)
        )

        message = notification_service.send.call_args.kwargs["message"]

        assert "Toyota Corolla" in message
        assert "20/05/2027 à 14:30" in message

    @pytest.mark.asyncio
    async def test_notification_uses_fallback_when_vehicle_is_missing(
        self,
        use_case,
        repository,
        notification_service,
    ):
        test_drive = self.create_test_drive(with_vehicle=False)
        self.configure_success(repository, test_drive)

        await use_case.execute(
            self.create_dto(status=TestDriveStatus.CONFIRMED)
        )

        message = notification_service.send.call_args.kwargs["message"]

        assert "véhicule non défini" in message

    @pytest.mark.asyncio
    async def test_notification_uses_fallback_when_date_is_missing(
        self,
        use_case,
        repository,
        notification_service,
    ):
        test_drive = self.create_test_drive()
        test_drive.appointment_date = None
        self.configure_success(repository, test_drive)

        await use_case.execute(
            self.create_dto(status=TestDriveStatus.CONFIRMED)
        )

        message = notification_service.send.call_args.kwargs["message"]

        assert "date non définie" in message

    @pytest.mark.asyncio
    async def test_does_not_notify_when_user_is_missing(
        self,
        use_case,
        repository,
        notification_service,
    ):
        test_drive = self.create_test_drive(with_user=False)
        self.configure_success(repository, test_drive)

        await use_case.execute(
            self.create_dto(status=TestDriveStatus.CONFIRMED)
        )

        notification_service.send.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_does_not_notify_when_notification_service_is_disabled(
        self,
        repository,
        user_repository,
        event_service,
        unit_of_work,
    ):
        test_drive = self.create_test_drive()
        repository.get_full_by_id.return_value = test_drive
        repository.update.side_effect = lambda entity: entity

        use_case = UpdateTestDriveStatusUseCase(
            repository=repository,
            user_repository=user_repository,
            event_service=event_service,
            unit_of_work=unit_of_work,
            notification_service=None,
        )

        result = await use_case.execute(
            self.create_dto(status=TestDriveStatus.CONFIRMED)
        )

        assert result.status == TestDriveStatus.CONFIRMED
        unit_of_work.commit.assert_called_once()

    # ==========================================================
    # ADMIN PENDING COUNT
    # ==========================================================

    @pytest.mark.asyncio
    async def test_updates_pending_count_after_commit(
        self,
        use_case,
        repository,
        user_repository,
        notification_service,
        unit_of_work,
    ):
        test_drive = self.create_test_drive()
        self.configure_success(repository, test_drive)

        admins = [
            SimpleNamespace(id=1),
            SimpleNamespace(id=2),
        ]
        user_repository.get_by_role.return_value = admins
        repository.count_pending.return_value = 5

        await use_case.execute(
            self.create_dto(status=TestDriveStatus.CONFIRMED)
        )

        unit_of_work.commit.assert_called_once()
        repository.count_pending.assert_called_once()
        user_repository.get_by_role.assert_called_once_with(
            UserRole.ADMIN
        )

        notification_service.send_update.assert_has_awaits(
            [
                call(
                    user_id="1",
                    payload={
                        "type": "TEST_DRIVE_PENDING_UPDATED",
                        "count": 5,
                    },
                ),
                call(
                    user_id="2",
                    payload={
                        "type": "TEST_DRIVE_PENDING_UPDATED",
                        "count": 5,
                    },
                ),
            ]
        )

    @pytest.mark.asyncio
    async def test_continues_when_admin_count_notification_fails(
        self,
        use_case,
        repository,
        user_repository,
        notification_service,
        unit_of_work,
    ):
        test_drive = self.create_test_drive()
        self.configure_success(repository, test_drive)

        admins = [
            SimpleNamespace(id=1),
            SimpleNamespace(id=2),
        ]
        user_repository.get_by_role.return_value = admins

        notification_service.send_update.side_effect = [
            Exception("Broadcast failed"),
            None,
        ]

        result = await use_case.execute(
            self.create_dto(status=TestDriveStatus.CONFIRMED)
        )

        assert result.status == TestDriveStatus.CONFIRMED
        assert notification_service.send_update.await_count == 2
        unit_of_work.commit.assert_called_once()
        unit_of_work.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_does_not_update_count_without_notification_service(
        self,
        repository,
        user_repository,
        event_service,
        unit_of_work,
    ):
        test_drive = self.create_test_drive()
        repository.get_full_by_id.return_value = test_drive
        repository.update.side_effect = lambda entity: entity

        use_case = UpdateTestDriveStatusUseCase(
            repository=repository,
            user_repository=user_repository,
            event_service=event_service,
            unit_of_work=unit_of_work,
            notification_service=None,
        )

        await use_case.execute(
            self.create_dto(status=TestDriveStatus.CONFIRMED)
        )

        repository.count_pending.assert_not_called()
        user_repository.get_by_role.assert_not_called()

    # ==========================================================
    # TRANSACTION / ROLLBACK
    # ==========================================================

    @pytest.mark.asyncio
    async def test_rolls_back_when_repository_update_fails(
        self,
        use_case,
        repository,
        unit_of_work,
    ):
        test_drive = self.create_test_drive()
        repository.get_full_by_id.return_value = test_drive
        repository.update.side_effect = Exception("Update failed")

        with pytest.raises(Exception, match="Update failed"):
            await use_case.execute(
                self.create_dto(status=TestDriveStatus.CONFIRMED)
            )

        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_rolls_back_when_event_logging_fails(
        self,
        use_case,
        repository,
        event_service,
        unit_of_work,
    ):
        test_drive = self.create_test_drive()
        self.configure_success(repository, test_drive)
        event_service.log.side_effect = Exception("Event failed")

        with pytest.raises(Exception, match="Event failed"):
            await use_case.execute(
                self.create_dto(status=TestDriveStatus.CONFIRMED)
            )

        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_rolls_back_when_customer_notification_fails(
        self,
        use_case,
        repository,
        notification_service,
        unit_of_work,
    ):
        test_drive = self.create_test_drive()
        self.configure_success(repository, test_drive)
        notification_service.send.side_effect = Exception(
            "Customer notification failed"
        )

        with pytest.raises(
            Exception,
            match="Customer notification failed",
        ):
            await use_case.execute(
                self.create_dto(status=TestDriveStatus.CONFIRMED)
            )

        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_rolls_back_when_commit_fails(
        self,
        use_case,
        repository,
        unit_of_work,
    ):
        test_drive = self.create_test_drive()
        self.configure_success(repository, test_drive)
        unit_of_work.commit.side_effect = Exception("Commit failed")

        with pytest.raises(Exception, match="Commit failed"):
            await use_case.execute(
                self.create_dto(status=TestDriveStatus.CONFIRMED)
            )

        unit_of_work.commit.assert_called_once()
        unit_of_work.rollback.assert_called_once()