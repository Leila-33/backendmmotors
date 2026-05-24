from modules.core.exceptions import TokenInvalid, TokenExpired

from jwt import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timezone, timedelta
from modules.auth.domain.entities.refresh_token import RefreshTokenEntity


class RefreshTokenUseCase:

    def __init__(self, refresh_repo, blacklist_repo, jwt_service):
        self.refresh_repo = refresh_repo
        self.blacklist_repo = blacklist_repo
        self.jwt = jwt_service

    def execute(self, refresh_token: str):

        print("REFRESH TOKEN RECEIVED:", refresh_token)

        # =========================
        # 1. blacklist check
        # =========================
        if self.blacklist_repo.exists(refresh_token):
            print("❌ BLACKLIST HIT")
            raise TokenInvalid()

        # =========================
        # 2. decode JWT
        # =========================
        try:
            payload = self.jwt.decode(refresh_token)
            print("✅ PAYLOAD:", payload)
        except ExpiredSignatureError:
            print("❌ TOKEN EXPIRED")
            raise TokenExpired()
        except InvalidTokenError:
            print("❌ INVALID SIGNATURE")
            raise TokenInvalid()

        if payload.get("type") != "refresh":
            print("❌ WRONG TYPE:", payload.get("type"))
            raise TokenInvalid()

        user_id = payload.get("sub")
        role = payload.get("role")
        jti = payload.get("jti")

        print("JTI:", jti)

        if not jti:
            print("❌ NO JTI IN TOKEN")
            raise TokenInvalid()

        # =========================
        # 3. DB check
        # =========================
        stored = self.refresh_repo.find_by_jti(jti)

        print("DB RESULT:", stored)

        if not stored:
            print("❌ JTI NOT FOUND IN DB")
            raise TokenInvalid()

        if stored.revoked:
            print("❌ TOKEN ALREADY REVOKED")
            raise TokenInvalid()

        # =========================
        # 4. revoke old session
        # =========================
        self.refresh_repo.revoke_by_jti(jti)

        now = datetime.now(timezone.utc)

        # =========================
        # 5. new tokens
        # =========================
        new_refresh = self.jwt.create_refresh_token(user_id, role)
        new_payload = self.jwt.decode(new_refresh)

        print("NEW JTI:", new_payload["jti"])

        new_access = self.jwt.create_access_token(user_id, role)

        # =========================
        # 6. save new session
        # =========================
        refresh_token_entity = RefreshTokenEntity(
            id=new_payload["jti"],
            user_id=user_id,
            role=role,
            jti=new_payload["jti"],
            expires_at=now + timedelta(days=7),
            created_at=now,
            revoked=False
        )

        self.refresh_repo.save(refresh_token_entity)

        return {
            "access_token": new_access,
            "refresh_token": new_refresh
        }