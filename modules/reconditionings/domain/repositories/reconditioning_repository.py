from abc import ABC, abstractmethod
from typing import Optional, List
from modules.reconditionings.domain.entities.reconditioning import Reconditioning


class ReconditioningRepository(ABC):

    @abstractmethod
    def get_by_id(self, reconditioning_id: str) -> Optional[Reconditioning]:
        pass

    @abstractmethod
    def get_by_vehicle_id(self, vehicle_id: str) -> Optional[Reconditioning]:
        pass

    @abstractmethod
    def save(self, reconditioning: Reconditioning) -> None:
        pass

    @abstractmethod
    def update(self, reconditioning: Reconditioning) -> None:
        pass