from sqlalchemy.orm import Session, joinedload
from modules.favorites.domain.repositories.favorite_repository import FavoriteRepository
from modules.favorites.infrastructure.db.favorite_model import FavoriteModel
from modules.favorites.infrastructure.mappers.favorite_mapper import FavoriteMapper

class FavoriteRepositorySQL(FavoriteRepository):


    def __init__(
        self,
        db: Session,
    ):

        self.db = db


    # =========================
    # ADD
    # =========================

    def add(
        self,
        favorite,
    ):

        model = FavoriteMapper.to_model(
            favorite
        )

        self.db.add(model)

        self.db.flush()

        return FavoriteMapper.to_domain(
            model
        )


    # =========================
    # DELETE
    # =========================

    def delete(
        self,
        user_id: str,
        vehicle_id: str,
    ):

        (
            self.db
            .query(FavoriteModel)
            .filter(
                FavoriteModel.user_id == user_id,
                FavoriteModel.vehicle_id == vehicle_id,
            )
            .delete()
        )


    # =========================
    # EXISTS
    # =========================

    def exists(
        self,
        user_id: str,
        vehicle_id: str,
    ) -> bool:

        return (

            self.db
            .query(FavoriteModel)
            .filter(
                FavoriteModel.user_id == user_id,
                FavoriteModel.vehicle_id == vehicle_id,
            )
            .first()

            is not None

        )


    # =========================
    # GET USER FAVORITES
    # =========================

    def get_user_favorites(
        self,
        user_id: str,
    ):

        models = (

            self.db
            .query(FavoriteModel)

            .options(
                joinedload(
                    FavoriteModel.vehicle
                )
            )

            .filter(
                FavoriteModel.user_id == user_id
            )

            .order_by(
                FavoriteModel.created_at.desc()
            )

            .all()

        )


        return [

            FavoriteMapper.to_domain(model)

            for model in models

        ]
