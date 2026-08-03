from abc import ABC, abstractmethod
from modules.auth.domain.entities.token_blacklist import TokenBlacklist


class TokenBlacklistRepository(ABC):


    # =========================
    # ADD
    # =========================

    @abstractmethod
    def add(
        self,
        token: TokenBlacklist
    ) -> TokenBlacklist:
        pass


    # =========================
    # EXISTS
    # =========================

    @abstractmethod
    def exists(
        self,
        token: str
    ) -> bool:
        pass