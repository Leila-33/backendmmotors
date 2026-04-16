from abc import ABC, abstractmethod
from typing import Optional
from modules.clients.domain.entities.user import User

class UserRepository(ABC):

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> None:
        pass