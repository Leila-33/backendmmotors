from modules.favorites.domain.exceptions import FavoriteNotFound
from modules.favorites.api.schemas import (
    RemoveFavoriteResponse,
)

class RemoveFavoriteUseCase:


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
        # CHECK EXISTENCE
        # =========================

        exists = (
            self.repository
            .exists(
                user_id=user_id,
                vehicle_id=vehicle_id,
            )
        )


        if not exists:

            raise FavoriteNotFound()


        # =========================
        # DELETE
        # =========================

        self.repository.delete(
            user_id=user_id,
            vehicle_id=vehicle_id,
        )


        # =========================
        # COMMIT
        # =========================

        self.unit_of_work.commit()



        # =========================
        # RESPONSE
        # =========================

        return RemoveFavoriteResponse(

            message="Favori supprimé avec succès."

        )