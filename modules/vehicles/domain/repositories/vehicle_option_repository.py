from abc import ABC, abstractmethod
from typing import List
from modules.vehicles.domain.entities.vehicle_option import VehicleOption


class VehicleOptionRepository(ABC):

    @abstractmethod
    def create(self, vehicle_option: VehicleOption):
        pass

    @abstractmethod
    def get_by_vehicle(self, vehicle_id: str) -> List[VehicleOption]:
        pass

    @abstractmethod
    def delete_by_vehicle(self, vehicle_id: str):
        pass