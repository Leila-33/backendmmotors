from modules.favorites.application.dtos.get_favorites_dto import (
    GetFavoritesDTO,
)
from modules.favorites.application.results.get_favorites_result import (
    GetFavoritesResult,
    FavoriteItemResult,
    FavoriteVehicleResult,
)


class GetFavoritesUseCase:

    def __init__(self, repository):
        self.repository = repository

    def execute(
        self,
        dto: GetFavoritesDTO,
    ) -> GetFavoritesResult:

        favorites = self.repository.get_user_favorites(
            dto.user_id
        )

        return GetFavoritesResult(
            items=[
                FavoriteItemResult(
                    id=f.id,
                    created_at=(
                        f.created_at.isoformat()
                        if f.created_at
                        else None
                    ),
                    vehicle=FavoriteVehicleResult(
                        id=f.vehicle.id,
                        brand=f.vehicle.brand,
                        model=f.vehicle.model,
                        year=f.vehicle.year,
                        price=f.vehicle.price,
                        mileage=f.vehicle.mileage,
                        type=f.vehicle.type,
                        images=f.vehicle.images or [],
                    ),
                )
                for f in favorites
            ]
        )