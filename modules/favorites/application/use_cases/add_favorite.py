from uuid import uuid4
from datetime import datetime, timezone

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
        dto: AddFavoriteDTO,
    ) -> AddFavoriteResult:

        try:

            # =========================
            # CHECK EXISTING
            # =========================

            if self.repository.exists(
                user_id=dto.user_id,
                vehicle_id=dto.vehicle_id,
            ):
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
            # RESULT
            # =========================

            return AddFavoriteResult(
                id=favorite.id,
            )

        except Exception:
            self.unit_of_work.rollback()
            raise