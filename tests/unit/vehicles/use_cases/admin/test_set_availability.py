import pytest
from unittest.mock import MagicMock

from modules.vehicles.application.dtos.admin.set_availability_dto import (
    SetAvailabilityDTO,
)
from modules.vehicles.application.use_cases.admin.set_availability import (
    SetAvailabilityUseCase,
)
from modules.vehicles.domain.enums import VehicleStatus
from modules.vehicles.domain.exceptions import (
    VehicleAvailabilityAlreadySet,
    VehicleCannotChangeAvailability,
    VehicleNotFound,
)
from modules.applications.domain.enums import EventType


class TestSetAvailabilityUseCase:

    @pytest.fixture
    def vehicle_repository(self):
        return MagicMock()

    @pytest.fixture
    def event_service(self):
        return MagicMock()

    @pytest.fixture
    def unit_of_work(self):
        return MagicMock()

    @pytest.fixture
    def use_case(
        self,
        vehicle_repository,
        event_service,
        unit_of_work,
    ):
        return SetAvailabilityUseCase(
            vehicle_repository=vehicle_repository,
            event_service=event_service,
            unit_of_work=unit_of_work,
        )

    @staticmethod
    def create_vehicle(
        vehicle_id=1,
        status=VehicleStatus.PUBLISHED,
        is_available=True,
    ):
        vehicle = MagicMock()

        vehicle.id = vehicle_id
        vehicle.status = status
        vehicle.is_available = is_available

        return vehicle

    @staticmethod
    def create_dto(
        vehicle_id=1,
        admin_id=10,
        value=False,
    ):
        return SetAvailabilityDTO(
            vehicle_id=vehicle_id,
            admin_id=admin_id,
            value=value,
        )

    # ==========================================================
    # SUCCESS
    # ==========================================================

    def test_sets_vehicle_available(
        self,
        use_case,
        vehicle_repository,
        event_service,
        unit_of_work,
    ):
        vehicle = self.create_vehicle(
            is_available=False,
        )

        dto = self.create_dto(
            value=True,
        )

        vehicle_repository.get_by_id.return_value = vehicle

        result = use_case.execute(dto)

        assert vehicle.is_available is True

        assert result.vehicle_id == vehicle.id
        assert result.status == vehicle.status.value
        assert result.is_available is True
        assert result.message == "Véhicule disponible"

        vehicle_repository.update.assert_called_once_with(
            vehicle
        )

        unit_of_work.commit.assert_called_once()
        unit_of_work.rollback.assert_not_called()

    def test_sets_vehicle_unavailable(
        self,
        use_case,
        vehicle_repository,
        event_service,
        unit_of_work,
    ):
        vehicle = self.create_vehicle(
            is_available=True,
        )

        dto = self.create_dto(
            value=False,
        )

        vehicle_repository.get_by_id.return_value = vehicle

        result = use_case.execute(dto)

        assert vehicle.is_available is False

        assert result.vehicle_id == vehicle.id
        assert result.status == vehicle.status.value
        assert result.is_available is False
        assert result.message == "Véhicule indisponible"

        vehicle_repository.update.assert_called_once_with(
            vehicle
        )

        unit_of_work.commit.assert_called_once()
        unit_of_work.rollback.assert_not_called()

    # ==========================================================
    # VEHICLE NOT FOUND
    # ==========================================================

    def test_raises_vehicle_not_found(
        self,
        use_case,
        vehicle_repository,
        event_service,
        unit_of_work,
    ):
        dto = self.create_dto()

        vehicle_repository.get_by_id.return_value = None

        with pytest.raises(VehicleNotFound):
            use_case.execute(dto)

        vehicle_repository.get_by_id.assert_called_once_with(
            dto.vehicle_id
        )

        vehicle_repository.update.assert_not_called()
        event_service.log.assert_not_called()
        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_not_called()

    # ==========================================================
    # SOLD VEHICLE
    # ==========================================================

    @pytest.mark.parametrize(
        "is_available,new_value",
        [
            (True, False),
            (False, True),
        ],
    )
    def test_cannot_change_availability_of_sold_vehicle(
        self,
        is_available,
        new_value,
        use_case,
        vehicle_repository,
        event_service,
        unit_of_work,
    ):
        vehicle = self.create_vehicle(
            status=VehicleStatus.SOLD,
            is_available=is_available,
        )

        dto = self.create_dto(
            value=new_value,
        )

        vehicle_repository.get_by_id.return_value = vehicle

        with pytest.raises(VehicleCannotChangeAvailability):
            use_case.execute(dto)

        vehicle_repository.update.assert_not_called()
        event_service.log.assert_not_called()
        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_not_called()

    # ==========================================================
    # ALREADY SET
    # ==========================================================

    @pytest.mark.parametrize(
        "current_value",
        [True, False],
    )
    def test_raises_when_availability_is_already_set(
        self,
        current_value,
        use_case,
        vehicle_repository,
        event_service,
        unit_of_work,
    ):
        vehicle = self.create_vehicle(
            is_available=current_value,
        )

        dto = self.create_dto(
            value=current_value,
        )

        vehicle_repository.get_by_id.return_value = vehicle

        with pytest.raises(VehicleAvailabilityAlreadySet):
            use_case.execute(dto)

        vehicle_repository.update.assert_not_called()
        event_service.log.assert_not_called()
        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_not_called()

    # ==========================================================
    # UPDATE
    # ==========================================================

    def test_updates_vehicle_with_new_availability(
        self,
        use_case,
        vehicle_repository,
    ):
        vehicle = self.create_vehicle(
            is_available=False,
        )

        dto = self.create_dto(
            value=True,
        )

        vehicle_repository.get_by_id.return_value = vehicle

        use_case.execute(dto)

        assert vehicle.is_available is True

        vehicle_repository.update.assert_called_once_with(
            vehicle
        )

    # ==========================================================
    # EVENT
    # ==========================================================

    def test_logs_availability_change_event(
        self,
        use_case,
        vehicle_repository,
        event_service,
        unit_of_work,
    ):
        vehicle = self.create_vehicle(
            vehicle_id=42,
            is_available=False,
        )

        dto = self.create_dto(
            vehicle_id=42,
            admin_id=10,
            value=True,
        )

        vehicle_repository.get_by_id.return_value = vehicle

        use_case.execute(dto)

        event_service.log.assert_called_once_with(
            type=EventType.VEHICLE_AVAILABILITY_CHANGED,
            message="Disponibilité du véhicule modifiée",
            vehicle_id=vehicle.id,
            user_id=dto.admin_id,
            event_metadata={
                "old_value": False,
                "new_value": True,
            },
        )

        unit_of_work.commit.assert_called_once()

    def test_event_contains_old_and_new_values(
        self,
        use_case,
        vehicle_repository,
        event_service,
    ):
        vehicle = self.create_vehicle(
            is_available=True,
        )

        dto = self.create_dto(
            value=False,
        )

        vehicle_repository.get_by_id.return_value = vehicle

        use_case.execute(dto)

        call_kwargs = event_service.log.call_args.kwargs

        assert call_kwargs["event_metadata"] == {
            "old_value": True,
            "new_value": False,
        }

    # ==========================================================
    # COMMIT
    # ==========================================================

    def test_commits_after_update_and_event(
        self,
        use_case,
        vehicle_repository,
        event_service,
        unit_of_work,
    ):
        vehicle = self.create_vehicle(
            is_available=False,
        )

        dto = self.create_dto(
            value=True,
        )

        vehicle_repository.get_by_id.return_value = vehicle

        use_case.execute(dto)

        vehicle_repository.update.assert_called_once_with(
            vehicle
        )
        event_service.log.assert_called_once()
        unit_of_work.commit.assert_called_once()

    # ==========================================================
    # UPDATE FAILURE
    # ==========================================================

    def test_rolls_back_when_update_fails(
        self,
        use_case,
        vehicle_repository,
        event_service,
        unit_of_work,
    ):
        vehicle = self.create_vehicle(
            is_available=False,
        )

        dto = self.create_dto(
            value=True,
        )

        vehicle_repository.get_by_id.return_value = vehicle

        vehicle_repository.update.side_effect = Exception(
            "Update failed"
        )

        with pytest.raises(
            Exception,
            match="Update failed",
        ):
            use_case.execute(dto)

        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

        event_service.log.assert_not_called()

    # ==========================================================
    # EVENT FAILURE
    # ==========================================================

    def test_rolls_back_when_event_logging_fails(
        self,
        use_case,
        vehicle_repository,
        event_service,
        unit_of_work,
    ):
        vehicle = self.create_vehicle(
            is_available=False,
        )

        dto = self.create_dto(
            value=True,
        )

        vehicle_repository.get_by_id.return_value = vehicle

        event_service.log.side_effect = Exception(
            "Event failed"
        )

        with pytest.raises(
            Exception,
            match="Event failed",
        ):
            use_case.execute(dto)

        vehicle_repository.update.assert_called_once_with(
            vehicle
        )

        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    # ==========================================================
    # COMMIT FAILURE
    # ==========================================================

    def test_rolls_back_when_commit_fails(
        self,
        use_case,
        vehicle_repository,
        event_service,
        unit_of_work,
    ):
        vehicle = self.create_vehicle(
            is_available=False,
        )

        dto = self.create_dto(
            value=True,
        )

        vehicle_repository.get_by_id.return_value = vehicle

        unit_of_work.commit.side_effect = Exception(
            "Commit failed"
        )

        with pytest.raises(
            Exception,
            match="Commit failed",
        ):
            use_case.execute(dto)

        unit_of_work.commit.assert_called_once()
        unit_of_work.rollback.assert_called_once()

    # ==========================================================
    # ORIGINAL VALUE
    # ==========================================================

    def test_preserves_old_value_for_event(
        self,
        use_case,
        vehicle_repository,
        event_service,
    ):
        vehicle = self.create_vehicle(
            is_available=False,
        )

        dto = self.create_dto(
            value=True,
        )

        vehicle_repository.get_by_id.return_value = vehicle

        use_case.execute(dto)

        call_kwargs = event_service.log.call_args.kwargs

        assert call_kwargs["event_metadata"]["old_value"] is False
        assert call_kwargs["event_metadata"]["new_value"] is True

    # ==========================================================
    # ADMIN ID
    # ==========================================================

    def test_event_uses_admin_id(
        self,
        use_case,
        vehicle_repository,
        event_service,
    ):
        vehicle = self.create_vehicle(
            is_available=False,
        )

        dto = self.create_dto(
            admin_id=999,
            value=True,
        )

        vehicle_repository.get_by_id.return_value = vehicle

        use_case.execute(dto)

        call_kwargs = event_service.log.call_args.kwargs

        assert call_kwargs["user_id"] == 999