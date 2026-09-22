from abc import ABC, abstractmethod


from abc import ABC, abstractmethod
from typing import List, Optional

from modules.test_drives.domain.entities.test_drive import TestDrive


class TestDriveRepository(ABC):

    # =========================
    # CREATE
    # =========================

    @abstractmethod
    def create(
        self,
        test_drive: TestDrive
    ) -> TestDrive:
        pass


    # =========================
    # AVAILABILITY
    # =========================

    @abstractmethod
    def find_conflicting_slot(
        self,
        vehicle_id: str,
        appointment_date
    ) -> Optional[TestDrive]:
        pass


    @abstractmethod
    def get_day_availability(
        self,
        vehicle_id: str,
        date
    ) -> dict:
        pass


    # =========================
    # READ
    # =========================

    @abstractmethod
    def get_by_id(
        self,
        test_drive_id: str
    ) -> Optional[TestDrive]:
        pass

    @abstractmethod
    def get_existing_for_user_vehicle(
        self,
        user_id: int,
        vehicle_id: int,
    ):
        pass

    @abstractmethod
    def has_existing_blocking_test_drive(
        self,
        user_id: int,
        vehicle_id: int,
    ) -> bool:
        pass

    @abstractmethod
    def get_by_user_id(
        self,
        user_id: str
    ) -> List[TestDrive]:
        pass


    @abstractmethod
    def get_full_by_id(
        self,
        test_drive_id: str
    ):
        """
        Retourne le modèle enrichi :
        - user
        - vehicle
        - events
        """
        pass

    def get_all_admin(
        self,
        status: str | None = None,
        search: str | None = None,
        page: int = 1,
        limit: int = 20
    ):
        pass

    # =========================
    # UPDATE
    # =========================

    @abstractmethod
    def update(
        self,
        test_drive: TestDrive
    ) -> TestDrive:
        pass


    # =========================
    # ADMIN / DASHBOARD
    # =========================

    @abstractmethod
    def count_pending(
        self
    ) -> int:
        pass