from abc import ABC, abstractmethod

class FavoriteRepository(ABC):

    @abstractmethod
    def add(self, favorite):
        pass

    @abstractmethod
    def delete(self, user_id: str, vehicle_id: str):
        pass

    @abstractmethod
    def exists(self, user_id: str, vehicle_id: str) -> bool:
        pass

    @abstractmethod
    def get_user_favorites(self, user_id: str):
        pass