from abc import ABC, abstractmethod


class BlacklistRepository(ABC):

    @abstractmethod
    def add(self, token: str) -> None:
        """Ajoute un token dans la blacklist"""
        pass

    @abstractmethod
    def exists(self, token: str) -> bool:
        """Vérifie si le token est blacklisté"""
        pass