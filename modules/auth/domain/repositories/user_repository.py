from abc import ABC, abstractmethod
from typing import Optional, Tuple, List
from modules.auth.domain.entities.user import User
from modules.auth.infrastructure.db.user_model import UserModel


class UserRepository(ABC):

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> None:
        pass

    @abstractmethod
    def update(self, user: User) -> None:
        pass

# repositories/interfaces/user_repository.py

    @abstractmethod
    def find_all(
        self,
        page: int,
        limit: int,
        search: Optional[str],
        role: Optional[str]
    ) -> Tuple[List[UserModel], int]:
        """
        Retourne:
            - liste des users
            - total count
        """
        pass