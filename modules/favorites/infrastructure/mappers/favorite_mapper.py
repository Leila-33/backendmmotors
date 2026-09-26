from modules.favorites.domain.entities.favorite import Favorite
from modules.favorites.infrastructure.db.favorite_model import FavoriteModel
from modules.vehicles.infrastructure.mappers.vehicle_mapper import VehicleMapper

class FavoriteMapper:


    # =========================
    # MODEL -> DOMAIN
    # =========================

    @staticmethod
    def to_domain(
        model: FavoriteModel,
    ) -> Favorite:

        return Favorite(

            id=model.id,

            user_id=model.user_id,

            vehicle_id=model.vehicle_id,

            created_at=model.created_at,
            
            vehicle=VehicleMapper.to_domain(model.vehicle)
        )


    # =========================
    # DOMAIN -> MODEL
    # =========================

    @staticmethod
    def to_model(
        favorite: Favorite,
    ) -> FavoriteModel:

        return FavoriteModel(

            id=favorite.id,

            user_id=favorite.user_id,

            vehicle_id=favorite.vehicle_id,

            created_at=favorite.created_at,

        )


    # =========================
    # UPDATE MODEL
    # =========================

    @staticmethod
    def update_model(
        model: Favorite,
        favorite: Favorite,
    ) -> Favorite:

        model.user_id = favorite.user_id
        model.vehicle_id = favorite.vehicle_id
        model.created_at = favorite.created_at

        return model