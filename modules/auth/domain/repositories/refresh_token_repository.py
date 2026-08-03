from abc import ABC, abstractmethod
from modules.auth.domain.entities.refresh_token import RefreshToken



class RefreshTokenRepository(ABC):


    # =========================
    # SAVE
    # =========================

    @abstractmethod
    def save(
        self,
        token: RefreshToken
    ) -> RefreshToken:
        pass


    # =========================
    # UPDATE
    # =========================

    @abstractmethod
    def update(
        self,
        token: RefreshToken
    ) -> RefreshToken | None:
        pass


    # =========================
    # FIND BY JTI
    # =========================

    @abstractmethod
    def find_by_jti(
        self,
        jti: str
    ) -> RefreshToken | None:
        pass


    # =========================
    # FIND BY USER
    # =========================

    @abstractmethod
    def find_by_user(
        self,
        user_id: str
    ) -> list[RefreshToken]:
        pass


    # =========================
    # REVOKE TOKEN
    # =========================

    @abstractmethod
    def revoke_by_jti(
        self,
        jti: str
    ) -> None:
        pass


    # =========================
    # REVOKE ALL USER TOKENS
    # =========================

    @abstractmethod
    def revoke_all_by_user(
        self,
        user_id: str
    ) -> None:
        pass