from abc import ABC, abstractmethod
from typing import List, Optional
from modules.vehicles.domain.entities.vehicle import Vehicle


class VehicleRepository(ABC):

    @abstractmethod
    def get_by_id(self, vehicle_id: str) -> Optional[Vehicle]:
        pass

    @abstractmethod
    def get_all(self) -> List[Vehicle]:
        pass

    @abstractmethod
    def save(self, vehicle: Vehicle) -> Vehicle:
        pass

    @abstractmethod
    def update(self, vehicle: Vehicle) -> Vehicle:
        pass

    @abstractmethod
    def delete(self, vehicle_id: str) -> None:
        pass