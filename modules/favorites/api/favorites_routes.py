from fastapi import APIRouter, Depends
from core.security.dependencies import get_current_user
from modules.favorites.api.schemas import GetFavoritesResponse

from modules.favorites.api.dependencies import (
    get_add_favorite_usecase,
    get_remove_favorite_usecase,
    get_favorites_usecase
)
router = APIRouter(tags=["favorites"])

@router.post("/{vehicle_id}")
def add_favorite(
    vehicle_id: str,
    user=Depends(get_current_user),
    usecase=Depends(get_add_favorite_usecase)
):
    return usecase.execute(user.id, vehicle_id)


@router.delete("/{vehicle_id}")
def remove_favorite(
    vehicle_id: str,
    user=Depends(get_current_user),
    usecase=Depends(get_remove_favorite_usecase)
):
    return usecase.execute(user.id, vehicle_id)


@router.get("/me", response_model=GetFavoritesResponse)
def get_favorites(
    user=Depends(get_current_user),
    usecase=Depends(get_favorites_usecase)
):

    return usecase.execute(user.id)