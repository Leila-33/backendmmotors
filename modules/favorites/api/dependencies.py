from fastapi import Depends

from modules.dependencies.dependencies import get_favorite_repository

from modules.favorites.application.use_cases.add_favorite import AddFavoriteUseCase
from modules.favorites.application.use_cases.remove_favorite import RemoveFavoriteUseCase
from modules.favorites.application.use_cases.get_favorites import GetFavoritesUseCase

from modules.favorites.domain.repositories.favorite_repository import FavoriteRepository
from core.database.dependencies import (
    get_unit_of_work
)

def get_add_favorite_usecase(
    repo: FavoriteRepository = Depends(get_favorite_repository),
        unit_of_work=Depends(
        get_unit_of_work
    ),
):
    return AddFavoriteUseCase(
        repository=repo,
        unit_of_work=unit_of_work,
)

def get_remove_favorite_usecase(
    repo: FavoriteRepository = Depends(get_favorite_repository),
        unit_of_work=Depends(
        get_unit_of_work
    ),
):
    return RemoveFavoriteUseCase(
        repository=repo,
        unit_of_work=unit_of_work,
)


def get_favorites_usecase(
    repo: FavoriteRepository = Depends(get_favorite_repository),
):
    return GetFavoritesUseCase(repo=repo)