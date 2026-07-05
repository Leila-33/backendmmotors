from abc import ABC, abstractmethod
from typing import Optional
from modules.inspections.domain.entities.inspection import Inspection


class InspectionRepository(ABC):

    @abstractmethod
    def save(self, inspection: Inspection) -> None:
        pass

    @abstractmethod
    def update(self, inspection: Inspection) -> None:
        pass

    @abstractmethod
    def get_by_id(self, inspection_id: str) -> Optional[Inspection]:
        pass

    @abstractmethod
    def get_by_vehicle_id(self, vehicle_id: str) -> Optional[Inspection]:
        pass