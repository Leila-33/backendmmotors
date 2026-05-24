from sqlalchemy.orm import Session, selectinload

from modules.favorites.domain.repositories.favorite_repository import FavoriteRepository
from modules.favorites.infrastructure.db.favorite_model import FavoriteModel


class FavoriteRepositorySQL(FavoriteRepository):

    def __init__(self, session: Session):
        self.session = session

    # =========================
    # ADD FAVORITE
    # =========================
    def add(self, favorite: FavoriteModel):
        self.session.add(favorite)

    # =========================
    # DELETE FAVORITE
    # =========================
    def delete(self, user_id: str, vehicle_id: str):
        self.session.query(FavoriteModel).filter(
            FavoriteModel.user_id == user_id,
            FavoriteModel.vehicle_id == vehicle_id
        ).delete(synchronize_session=False)

    # =========================
    # EXISTS CHECK
    # =========================
    def exists(self, user_id: str, vehicle_id: str) -> bool:
        return (
            self.session.query(FavoriteModel)
            .filter(
                FavoriteModel.user_id == user_id,
                FavoriteModel.vehicle_id == vehicle_id
            )
            .first()
            is not None
        )

    # =========================
    # GET USER FAVORITES
    # =========================
    def get_user_favorites(self, user_id: str):

        return (
            self.session.query(FavoriteModel)
            .options(
                selectinload(FavoriteModel.vehicle)
            )
            .filter(
                FavoriteModel.user_id == user_id
            )
            .all()
    )

    # =========================
    # COMMIT
    # =========================
    def commit(self):
        self.session.commit()