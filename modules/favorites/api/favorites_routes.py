from fastapi import APIRouter, Depends, status
from core.security.dependencies import get_current_user

from modules.favorites.application.use_cases.add_favorite import (
    AddFavoriteUseCase,
)
from modules.favorites.application.use_cases.remove_favorite import (
    RemoveFavoriteUseCase,
)
from modules.favorites.api.schemas import (
    AddFavoriteResponse,
    GetFavoritesResponse,
    RemoveFavoriteResponse
)
from modules.favorites.api.dependencies import (
    get_add_favorite_usecase,
    get_remove_favorite_usecase,
    get_favorites_usecase
)
router = APIRouter(tags=["favorites"])

@router.post(
    "/{vehicle_id}",
    response_model=AddFavoriteResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_favorite(
    vehicle_id: str,
    current_user=Depends(get_current_user),
    use_case: AddFavoriteUseCase = Depends(
        get_add_favorite_usecase
    ),
):

    return use_case.execute(
        user_id=current_user.id,
        vehicle_id=vehicle_id,
    )

@router.delete(
    "/{vehicle_id}",
    response_model=RemoveFavoriteResponse,
)
def remove_favorite(
    vehicle_id: str,
    current_user=Depends(get_current_user),
    use_case: RemoveFavoriteUseCase = Depends(
        get_remove_favorite_usecase
    ),
):

    return use_case.execute(

        user_id=current_user.id,

        vehicle_id=vehicle_id

    )


@router.get("/me", response_model=GetFavoritesResponse)
def get_favorites(
    user=Depends(get_current_user),
    usecase=Depends(get_favorites_usecase)
):

    return usecase.execute(user.id)