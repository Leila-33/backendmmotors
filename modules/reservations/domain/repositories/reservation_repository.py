from abc import ABC, abstractmethod


class ReservationRepository(ABC):

    @abstractmethod
    def create(self, data): pass

    @abstractmethod
    def get_by_id(self, reservation_id): pass

    @abstractmethod
    def get_by_user(self, user_id): pass

    @abstractmethod
    def get_all(self): pass

    @abstractmethod
    def cancel(self, reservation_id): pass

    @abstractmethod
    def exists_overlap(self, vehicle_id, start_date, end_date): pass