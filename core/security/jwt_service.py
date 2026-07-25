from datetime import datetime, timedelta, timezone
import jwt
import uuid
from modules.auth.domain.exceptions import TokenInvalid, TokenExpired


class JwtService:

    def __init__(self, secret: str, algorithm: str = "HS256"):
        self.secret = secret
        self.algorithm = algorithm

    def create_access_token(self, user_id: str, role: str) -> str:
        payload = {
            "sub": user_id,
            "role": role,
            "type": "access",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15)
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: str, role: str) -> str:
        payload = {
            "sub": user_id,
            "role": role,
            "type": "refresh",
            "jti": str(uuid.uuid4()),  # 🔥 UNIQUE
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(days=7)
        }

        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def create_email_token(self, user_id: str) -> str:
        payload = {
            "sub": user_id,
            "type": "email_verification",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def decode(self, token: str, type_expected: str | None = None):
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm]
            )

        except jwt.ExpiredSignatureError:
            raise TokenExpired()

        except jwt.InvalidTokenError:
            raise TokenInvalid()

        if "sub" not in payload:
            raise TokenInvalid()

        if type_expected and payload.get("type") != type_expected:
            raise TokenInvalid()

        return payload