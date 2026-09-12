import logging
from modules.favorites.application.dtos.remove_favorite_dto import (
    RemoveFavoriteDTO,
)
from modules.favorites.application.results.remove_favorite_result import (
    RemoveFavoriteResult,
)
from modules.favorites.domain.exceptions import FavoriteNotFound


logger = logging.getLogger(__name__)

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
            if not self.repository.exists(
                user_id=dto.user_id,
                vehicle_id=dto.vehicle_id,
            ):
                logger.warning(
                    "Tentative de suppression "
                    "d'un favori inexistant",
                    extra={
                        "user_id": dto.user_id,
                        "vehicle_id": dto.vehicle_id,
                    },
                )
                raise FavoriteNotFound()

            self.repository.delete(
                user_id=dto.user_id,
                vehicle_id=dto.vehicle_id,
            )

            self.unit_of_work.commit()

            logger.info(
                "Véhicule retiré des favoris",
                extra={
                    "user_id": dto.user_id,
                    "vehicle_id": dto.vehicle_id,
                },
            )

            return RemoveFavoriteResult(
                message="Favori supprimé avec succès.",
            )

        except FavoriteNotFound:
            self.unit_of_work.rollback()
            raise

        except Exception:
            self.unit_of_work.rollback()
            logger.exception(
                "Erreur lors de la suppression "
                "du véhicule des favoris",
                extra={
                    "user_id": dto.user_id,
                    "vehicle_id": dto.vehicle_id,
                },
            )
            raise