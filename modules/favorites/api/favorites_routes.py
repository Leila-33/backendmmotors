from fastapi import APIRouter, Depends, status

from core.security.dependencies import get_current_user
from modules.auth.domain.entities.user import User

from modules.favorites.api.dependencies import (
    get_add_favorite_usecase,
    get_remove_favorite_usecase,
    get_get_favorites_usecase,
)

from modules.favorites.api.schemas import (
    AddFavoriteResponse,
    RemoveFavoriteResponse,
    GetFavoritesResponse,
    FavoriteItemResponse,
    FavoriteVehicleResponse,
)

from modules.favorites.application.dtos.add_favorite_dto import (
    AddFavoriteDTO,
)
from modules.favorites.application.dtos.remove_favorite_dto import (
    RemoveFavoriteDTO,
)
from modules.favorites.application.dtos.get_favorites_dto import (
    GetFavoritesDTO,
)
from modules.favorites.application.use_cases.add_favorite import (
    AddFavoriteUseCase,
)
from modules.favorites.application.use_cases.remove_favorite import (
    RemoveFavoriteUseCase,
)
from modules.favorites.application.use_cases.get_favorites import (
    GetFavoritesUseCase,
)


router = APIRouter(
    tags=["favorites"]
)


# ============================================================
# ADD FAVORITE
# ============================================================

@router.post(
    "/{vehicle_id}",
    response_model=AddFavoriteResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_favorite(
    vehicle_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    usecase: AddFavoriteUseCase = Depends(
        get_add_favorite_usecase
    ),
):
    dto = AddFavoriteDTO(
        user_id=current_user.id,
        vehicle_id=vehicle_id,
    )

    result = usecase.execute(dto)

    return AddFavoriteResponse(
        id=result.id,
        message="Favori ajouté avec succès.",
    )


# ============================================================
# REMOVE FAVORITE
# ============================================================

@router.delete(
    "/{vehicle_id}",
    response_model=RemoveFavoriteResponse,
)
def remove_favorite(
    vehicle_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    usecase: RemoveFavoriteUseCase = Depends(
        get_remove_favorite_usecase
    ),
):
    dto = RemoveFavoriteDTO(
        user_id=current_user.id,
        vehicle_id=vehicle_id,
    )

    result = usecase.execute(dto)

    return RemoveFavoriteResponse(
        message=result.message,
    )


# ============================================================
# GET MY FAVORITES
# ============================================================

@router.get(
    "/me",
    response_model=GetFavoritesResponse,
)
def get_favorites(
    current_user: User = Depends(
        get_current_user
    ),
    usecase: GetFavoritesUseCase = Depends(
        get_get_favorites_usecase
    ),
):
    dto = GetFavoritesDTO(
    user_id=current_user.id,
)

    result = usecase.execute(dto)

    return GetFavoritesResponse(
        items=[
            FavoriteItemResponse(
                id=item.id,
                created_at=item.created_at,
                vehicle=FavoriteVehicleResponse(
                    id=item.vehicle.id,
                    brand=item.vehicle.brand,
                    model=item.vehicle.model,
                    year=item.vehicle.year,
                    price=item.vehicle.price,
                    mileage=item.vehicle.mileage,
                    type=item.vehicle.type,
                    images=item.vehicle.images,
                ),
            )
            for item in result.items
        ]
    )