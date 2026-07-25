from uuid import uuid4
from datetime import datetime, timezone
from modules.favorites.domain.exceptions import FavoriteAlreadyExists
from modules.favorites.domain.entities.favorite import Favorite
from modules.favorites.api.schemas import (
    AddFavoriteResponse,
)


class AddFavoriteUseCase:


    def __init__(
        self,
        repository,
        unit_of_work,
    ):

        self.repository = repository
        self.unit_of_work = unit_of_work



    def execute(
        self,
        user_id: str,
        vehicle_id: str,
    ):


        # =========================
        # CHECK EXISTING
        # =========================

        if self.repository.exists(
            user_id=user_id,
            vehicle_id=vehicle_id,
        ):

            raise FavoriteAlreadyExists()


        # =========================
        # CREATE DOMAIN
        # =========================

        favorite = Favorite(

            id=str(uuid4()),

            user_id=user_id,

            vehicle_id=vehicle_id,

            created_at=datetime.now(
                timezone.utc
            ),

        )


        # =========================
        # SAVE
        # =========================

        favorite = self.repository.add(
            favorite
        )

        self.unit_of_work.commit()


        # =========================
        # RESPONSE
        # =========================

        return AddFavoriteResponse(

            id=favorite.id,

            message="Favori ajouté avec succès."

        )