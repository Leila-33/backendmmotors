from abc import ABC, abstractmethod
from datetime import date, datetime
from modules.reservations.domain.entities.reservation import Reservation
from modules.reservations.domain.enums import ReservationStatus

class ReservationRepository(ABC):


    @abstractmethod
    def get_by_id(self, reservation_id): pass

    @abstractmethod
    def cancel(self, reservation_id): pass

    @abstractmethod
    def exists_overlap(self, vehicle_id, start_date, end_date): pass
   
    @abstractmethod
    def create_or_update(
        self,
        application_id: str,
        vehicle_id: str,
        start_date: date,
        end_date: date,
        status: ReservationStatus
    ) -> Reservation:
        pass

    @abstractmethod
    def delete_by_application(self, application_id: str): pass

    @abstractmethod
    def find_expired_active(
        self,
        now: datetime,
    ) -> list[Reservation]:
        pass

    @abstractmethod
    def get_by_application_id(
        self,
        application_id: str
    ) -> Reservation | None:
        pass

    @abstractmethod
    def get_active_by_vehicle_id(
        self,
        vehicle_id: str
    ) -> list[Reservation]:
        pass

    @abstractmethod
    def update(
        self,
        reservation: Reservation,
    ) -> Reservation:
        pass