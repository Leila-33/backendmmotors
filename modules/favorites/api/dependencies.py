# modules/favorites/infrastructure/dependencies.py

from fastapi import Depends

from modules.core.infrastructure.dependencies import get_favorite_repository

from modules.favorites.application.use_cases.add_favorite import AddFavoriteUseCase
from modules.favorites.application.use_cases.remove_favorite import RemoveFavoriteUseCase
from modules.favorites.application.use_cases.get_favorites import GetFavoritesUseCase

from modules.favorites.domain.repositories.favorite_repository import FavoriteRepository


def get_add_favorite_usecase(
    repo: FavoriteRepository = Depends(get_favorite_repository),
):
    return AddFavoriteUseCase(favorite_repository=repo)


def get_remove_favorite_usecase(
    repo: FavoriteRepository = Depends(get_favorite_repository),
):
    return RemoveFavoriteUseCase(favorite_repository=repo)


def get_favorites_usecase(
    repo: FavoriteRepository = Depends(get_favorite_repository),
):
    return GetFavoritesUseCase(repo=repo)