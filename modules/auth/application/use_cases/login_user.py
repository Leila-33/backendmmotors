from modules.core.exceptions import (
    InvalidCredentials,
    AccountDisabled,
    EmailNotVerified
)
from core.security.password import verify_password


from datetime import datetime, timezone, timedelta
from modules.auth.domain.entities.refresh_token import RefreshTokenEntity


class LoginUser:

    def __init__(self, user_repo, jwt_service, refresh_repo):
        self.user_repo = user_repo
        self.jwt = jwt_service
        self.refresh_repo = refresh_repo

    def execute(self, data):

        # =========================
        # 1. GET USER
        # =========================
        user = self.user_repo.get_by_email(data.email)

        if not user or not verify_password(data.password, user.password):
            raise InvalidCredentials()

        if not user.is_active:
            raise AccountDisabled()

        if not user.is_verified:
            raise EmailNotVerified()

        now = datetime.now(timezone.utc)

        # =========================
        # 2. CREATE TOKENS (WITH JTI INSIDE)
        # =========================
        access = self.jwt.create_access_token(user.id, user.role)
        refresh_token_str = self.jwt.create_refresh_token(user.id, user.role)

        payload = self.jwt.decode(refresh_token_str)
        jti = payload["jti"]

        # =========================
        # 3. SAVE SESSION (JTI BASED)
        # =========================
        refresh_token = RefreshTokenEntity(
            id=jti,
            user_id=user.id,
            role=user.role,
            jti=jti,
            expires_at=now + timedelta(days=7),
            created_at=now,
            revoked=False
        )

        self.refresh_repo.save(refresh_token)

        # =========================
        # 4. RESPONSE
        # =========================
        return {
            "access_token": access,
            "refresh_token": refresh_token_str
        }