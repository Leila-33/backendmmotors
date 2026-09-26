from modules.favorites.api.schemas import (
    FavoriteItemResponse,
    FavoriteVehicleResponse,
)
from modules.favorites.application.results.get_favorites_result import FavoriteItemResult
from modules.vehicles.infrastructure.mappers.vehicle_response_mapper import VehicleResponseMapper

class FavoriteResponseMapper:

    def __init__(
        self,
        vehicle_response_mapper: VehicleResponseMapper,
    ):
        self.vehicle_response_mapper = (
            vehicle_response_mapper
        )

    def to_response(
        self,
        item: FavoriteItemResult,
    ) -> FavoriteItemResponse:

        vehicle = item.vehicle

        return FavoriteItemResponse(
            id=item.id,
            created_at=item.created_at,

            vehicle=FavoriteVehicleResponse(
                id=vehicle.id,
                brand=vehicle.brand,
                model=vehicle.model,
                year=vehicle.year,
                price=vehicle.price,
                mileage=vehicle.mileage,
                type=vehicle.type,

                # Réutilisation du mapping des images
                # déjà centralisé dans VehicleResponseMapper.
                images=self.vehicle_response_mapper.map_images(
                    vehicle.images
                ),
            ),
        )

    def to_response_list(
        self,
        items: list[FavoriteItemResult],
    ) -> list[FavoriteItemResponse]:

        return [
            self.to_response(item)
            for item in items
        ]