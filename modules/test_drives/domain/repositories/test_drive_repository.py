from abc import ABC, abstractmethod


class TestDriveRepository(ABC):

    @abstractmethod
    def create(self, test_drive):
        pass

    @abstractmethod
    def find_conflicting_slot(self, vehicle_id, appointment_date):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def get_by_id(self, test_drive_id: str):
        pass


    @abstractmethod
    def update(self, test_drive):
        pass