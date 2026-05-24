from abc import ABC, abstractmethod
from typing import Optional
from modules.auth.domain.entities.refresh_token import RefreshTokenEntity


class RefreshRepository(ABC):

    @abstractmethod
    def save(self, token: RefreshTokenEntity) -> None:
        """Sauvegarde un refresh token"""
        pass

    @abstractmethod
    def find(self, token: str) -> Optional[RefreshTokenEntity]:
        """Récupère un refresh token"""
        pass

    @abstractmethod
    def revoke(self, token: str) -> None:
        """Révoque un refresh token"""
        pass