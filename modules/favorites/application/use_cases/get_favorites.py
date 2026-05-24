from modules.favorites.api.schemas import GetFavoritesResponse, FavoriteSchema, FavoriteVehicleSchema
class GetFavoritesUseCase:

    def __init__(self, repo):
        self.repo = repo

    def execute(self, user_id):

        favorites = self.repo.get_user_favorites(user_id)

        return GetFavoritesResponse(
            items=[
                FavoriteSchema(
                    id=f.id,
                    created_at=(
                        f.created_at.isoformat()
                        if f.created_at else None
                    ),
                    vehicle=FavoriteVehicleSchema(
                        id=f.vehicle.id,
                        brand=f.vehicle.brand,
                        model=f.vehicle.model,
                        year=f.vehicle.year,
                        price=f.vehicle.price,
                        mileage=f.vehicle.mileage,
                        type=f.vehicle.type,
                        images=f.vehicle.images or []
                    )
                )
                for f in favorites
            ]
        )