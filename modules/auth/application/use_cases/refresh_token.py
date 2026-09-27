import logging

from datetime import datetime, timedelta, timezone

from jwt import ExpiredSignatureError, InvalidTokenError

from modules.auth.application.results.refresh_tokens_result import RefreshTokensResult
from modules.auth.domain.entities.refresh_token import RefreshToken
from modules.auth.domain.enums import UserRole
from modules.auth.domain.exceptions import (
    TokenInvalid,
    TokenExpired,
)

logger = logging.getLogger(__name__)

class RefreshTokenUseCase:
    """
    Renouvelle les jetons d'authentification à partir d'un refresh token
    valide.

    Le refresh token utilisé est révoqué et remplacé par un nouveau
    afin de maintenir une rotation des tokens.
    """
    def __init__(
        self,
        refresh_repo,
        jwt_service,
        uow,
    ):
        self.refresh_repo = refresh_repo
        self.jwt = jwt_service
        self.uow = uow

    def execute(
        self,
        refresh_token: str,
    ) -> RefreshTokensResult:

        try:

            # =========================
            # DECODE JWT
            # =========================

            try:
                payload = self.jwt.decode(
                    refresh_token
                )

            except ExpiredSignatureError:
                raise TokenExpired()

            except InvalidTokenError:
                raise TokenInvalid()

            # =========================
            # VALIDATE TOKEN
            # =========================

            if payload.get("type") != "refresh":
                raise TokenInvalid()

            user_id = payload.get("sub")
            role_value = payload.get("role")
            jti = payload.get("jti")

            if not all([
                user_id,
                role_value,
                jti,
            ]):
                raise TokenInvalid()

            try:
                role = UserRole(role_value)
            except ValueError:
                raise TokenInvalid()

            # =========================
            # CHECK DATABASE
            # =========================

            stored = (
                self.refresh_repo
                .find_by_jti(jti)
            )

            if not stored:
                raise TokenInvalid()

            if stored.revoked:
                raise TokenInvalid()

            now = datetime.now(timezone.utc)

            if stored.expires_at <= now:
                raise TokenExpired()

            # =========================
            # REVOKE CURRENT TOKEN
            # =========================

            self.refresh_repo.revoke_by_jti(
                jti
            )

            # =========================
            # CREATE NEW TOKENS
            # =========================

            new_access = (
                self.jwt.create_access_token(
                    user_id,
                    role,
                )
            )

            new_refresh = (
                self.jwt.create_refresh_token(
                    user_id,
                    role,
                )
            )

            new_payload = self.jwt.decode(
                new_refresh
            )

            # =========================
            # SAVE NEW REFRESH TOKEN
            # =========================

            self.refresh_repo.save(
                RefreshToken(
                    id=new_payload["jti"],
                    user_id=user_id,
                    role=role,
                    jti=new_payload["jti"],
                    expires_at=(
                        now + timedelta(days=7)
                    ),
                    created_at=now,
                    revoked=False,
                )
            )

            # =========================
            # COMMIT
            # =========================

            self.uow.commit()

            # =========================
            # RESULT
            # =========================

            return RefreshTokensResult(
                access_token=new_access,
                refresh_token=new_refresh,
            )

        except Exception:
            self.uow.rollback()

            logger.exception(
                "Échec du renouvellement du refresh token"
            )

            raise