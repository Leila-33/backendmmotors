from abc import ABC, abstractmethod
from typing import List, Optional
from modules.vehicles.domain.entities.vehicle import Vehicle

class VehicleRepository(ABC):

    @abstractmethod
    def search(self, filters: dict) -> List[Vehicle]:
        pass
    
    @abstractmethod
    def get_by_id(self, vehicle_id: str) -> Optional[Vehicle]:
        pass