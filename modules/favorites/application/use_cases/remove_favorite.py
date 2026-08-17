from modules.favorites.application.dtos.remove_favorite_dto import (
    RemoveFavoriteDTO,
)
from modules.favorites.application.results.remove_favorite_result import (
    RemoveFavoriteResult,
)
from modules.favorites.domain.exceptions import FavoriteNotFound


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
        dto: RemoveFavoriteDTO,
    ) -> RemoveFavoriteResult:

        try:

            # =========================
            # CHECK EXISTENCE
            # =========================

            if not self.repository.exists(
                user_id=dto.user_id,
                vehicle_id=dto.vehicle_id,
            ):
                raise FavoriteNotFound()

            # =========================
            # DELETE
            # =========================

            self.repository.delete(
                user_id=dto.user_id,
                vehicle_id=dto.vehicle_id,
            )

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

            # =========================
            # RESULT
            # =========================

            return RemoveFavoriteResult(
                message="Favori supprimé avec succès.",
            )

        except Exception:
            self.unit_of_work.rollback()
            raise