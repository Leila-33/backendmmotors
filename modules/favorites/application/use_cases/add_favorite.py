from uuid import uuid4
from datetime import datetime, timezone
import logging

from modules.favorites.domain.exceptions import (
    FavoriteAlreadyExists,
)
from modules.favorites.domain.entities.favorite import Favorite
from modules.favorites.application.dtos.add_favorite_dto import (
    AddFavoriteDTO,
)
from modules.favorites.application.results.add_favorite_result import (
    AddFavoriteResult,
)

from modules.vehicles.domain.exceptions import (
    VehicleNotFound,
)
logger = logging.getLogger(__name__)


class AddFavoriteUseCase:

    def __init__(
        self,
        repository,
        vehicle_repository,
        unit_of_work,
    ):
        self.repository = repository
        self.vehicle_repository = vehicle_repository
        self.unit_of_work = unit_of_work

    def execute(
        self,
        dto: AddFavoriteDTO,
    ) -> AddFavoriteResult:

        try:
            # =========================
            # CHECK VEHICLE
            # =========================

            vehicle = self.vehicle_repository.get_by_id(
                dto.vehicle_id
            )

            if not vehicle:
                logger.warning(
                    "Tentative d'ajout aux favoris "
                    "pour un véhicule inexistant",
                    extra={
                        "user_id": dto.user_id,
                        "vehicle_id": dto.vehicle_id,
                    },
                )
                raise VehicleNotFound()

            # =========================
            # CHECK EXISTING
            # =========================

            if self.repository.exists(
                user_id=dto.user_id,
                vehicle_id=dto.vehicle_id,
            ):
                logger.info(
                    "Tentative d'ajout d'un véhicule "
                    "déjà présent dans les favoris",
                    extra={
                        "user_id": dto.user_id,
                        "vehicle_id": dto.vehicle_id,
                    },
                )
                raise FavoriteAlreadyExists()

            # =========================
            # CREATE DOMAIN ENTITY
            # =========================

            favorite = Favorite(
                id=str(uuid4()),
                user_id=dto.user_id,
                vehicle_id=dto.vehicle_id,
                created_at=datetime.now(timezone.utc),
            )

            # =========================
            # SAVE
            # =========================

            favorite = self.repository.add(
                favorite
            )

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

            # =========================
            # LOG SUCCESS
            # =========================

            logger.info(
                "Véhicule ajouté aux favoris",
                extra={
                    "favorite_id": favorite.id,
                    "user_id": dto.user_id,
                    "vehicle_id": dto.vehicle_id,
                },
            )

            # =========================
            # RESULT
            # =========================

            return AddFavoriteResult(
                id=favorite.id,
            )

        except Exception:
            self.unit_of_work.rollback()

            logger.exception(
                "Erreur lors de l'ajout du véhicule aux favoris",
                extra={
                    "user_id": dto.user_id,
                    "vehicle_id": dto.vehicle_id,
                },
            )

            raise