from modules.auth.infrastructure.db.refresh_model import RefreshTokenModel
from modules.auth.domain.entities.refresh_token import RefreshTokenEntity


class RefreshRepositorySQL:

    def __init__(self, db):
        self.db = db

    # =========================
    # SAVE
    # =========================
    def save(self, refresh_obj: RefreshTokenEntity):
        model = RefreshTokenModel(
            id=refresh_obj.id,
            user_id=refresh_obj.user_id,
            role=refresh_obj.role,
            jti=refresh_obj.jti,
            expires_at=refresh_obj.expires_at,
            revoked=refresh_obj.revoked,
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return model

    # =========================
    # FIND BY JTI
    # =========================
    def find_by_jti(self, jti: str):
        return (
            self.db.query(RefreshTokenModel)
            .filter(RefreshTokenModel.jti == jti)
            .first()
        )

    # =========================
    # FIND BY USER (optionnel)
    # =========================
    def find_by_user(self, user_id: str):
        return (
            self.db.query(RefreshTokenModel)
            .filter(RefreshTokenModel.user_id == user_id, RefreshTokenModel.revoked == False)
            .all()
        )

    # =========================
    # REVOKE BY JTI
    # =========================
    def revoke_by_jti(self, jti: str):
        token = self.find_by_jti(jti)

        if token:
            token.revoked = True
            self.db.commit()

    # =========================
    # REVOKE ALL USER SESSIONS (bonus)
    # =========================
    def revoke_all_by_user(self, user_id: str):
        (
            self.db.query(RefreshTokenModel)
            .filter(RefreshTokenModel.user_id == user_id)
            .update({"revoked": True})
        )

        self.db.commit()

    # =========================
    # EXISTS (anti-blacklist)
    # =========================
    def exists_jti(self, jti: str) -> bool:
        return (
            self.db.query(RefreshTokenModel)
            .filter(RefreshTokenModel.jti == jti, RefreshTokenModel.revoked == True)
            .first()
            is not None
        )