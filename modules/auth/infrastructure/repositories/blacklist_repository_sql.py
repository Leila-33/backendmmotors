
from sqlalchemy.orm import Session
from modules.auth.infrastructure.db.token_blacklist_model import TokenBlacklistModel


class BlacklistRepositorySQL:

    def __init__(self, db: Session):
        self.db = db
        
    def add(self, token: str):
        black = TokenBlacklistModel(token=token)
        self.db.add(black)
        self.db.commit()

    def exists(self, token: str) -> bool:
        return (
            self.db.query(TokenBlacklistModel)
            .filter_by(token=token)
            .first()
            is not None
        )