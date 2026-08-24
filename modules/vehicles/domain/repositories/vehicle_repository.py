from abc import ABC, abstractmethod

from modules.vehicles.domain.entities.vehicle import Vehicle
from modules.vehicles.application.dtos.vehicle_search_filters_dto import (
    VehicleSearchFiltersDTO,
)


class VehicleRepository(ABC):

    @abstractmethod
    def save(
        self,
        vehicle: Vehicle,
    ) -> Vehicle:
        pass

    @abstractmethod
    def get_by_id(
        self,
        vehicle_id: str,
    ) -> Vehicle | None:
        pass

    @abstractmethod
    def get_by_license_plate(
        self,
        plate: str,
    ) -> Vehicle | None:
        pass

    @abstractmethod
    def update(
        self,
        vehicle: Vehicle,
    ) -> Vehicle:
        pass

    @abstractmethod
    def delete(
        self,
        vehicle_id: str,
    ) -> None:
        pass

    @abstractmethod
    def search(
        self,
        filters: VehicleSearchFiltersDTO,
    ) -> tuple[list[Vehicle], int]:
        pass