from abc import ABC, abstractmethod
from typing import Optional, List

from modules.warranties.domain.entities.vehicle_warranty import VehicleWarranty


class VehicleWarrantyRepository(ABC):

    @abstractmethod
    def save(self, warranty: VehicleWarranty) -> VehicleWarranty:
        pass

    @abstractmethod
    def get_by_id(self, warranty_id: str) -> Optional[VehicleWarranty]:
        pass

    @abstractmethod
    def get_by_vehicle_id(self, vehicle_id: str) -> Optional[VehicleWarranty]:
        pass

    @abstractmethod
    def update(self, warranty: VehicleWarranty) -> VehicleWarranty:
        pass

    @abstractmethod
    def delete(self, warranty_id: str):
        pass