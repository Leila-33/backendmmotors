from fastapi import Depends

from core.database.dependencies import get_unit_of_work

from modules.dependencies.dependencies import (
    get_favorite_repository,
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

from modules.favorites.domain.repositories.favorite_repository import (
    FavoriteRepository,
)


# ============================================================
# ADD FAVORITE
# ============================================================

def get_add_favorite_usecase(
    repository: FavoriteRepository = Depends(
        get_favorite_repository
    ),
    unit_of_work=Depends(
        get_unit_of_work
    ),
):
    return AddFavoriteUseCase(
        repository=repository,
        unit_of_work=unit_of_work,
    )


# ============================================================
# REMOVE FAVORITE
# ============================================================

def get_remove_favorite_usecase(
    repository: FavoriteRepository = Depends(
        get_favorite_repository
    ),
    unit_of_work=Depends(
        get_unit_of_work
    ),
):
    return RemoveFavoriteUseCase(
        repository=repository,
        unit_of_work=unit_of_work,
    )


# ============================================================
# GET FAVORITES
# ============================================================

def get_get_favorites_usecase(
    repository: FavoriteRepository = Depends(
        get_favorite_repository
    ),
):
    return GetFavoritesUseCase(
        repository=repository,
    )