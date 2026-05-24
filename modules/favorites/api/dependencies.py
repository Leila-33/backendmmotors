# modules/favorites/infrastructure/dependencies.py

from infrastructure.db.dependencies import get_db
from modules.favorites.infrastructure.repositories.favorite_repository_sql import FavoriteRepositorySQL

from sqlalchemy.orm import Session


from modules.favorites.application.use_cases.add_favorite import AddFavoriteUseCase
from fastapi import Depends

def get_favorite_repository(db: Session = Depends(get_db)):
    return FavoriteRepositorySQL(db)



def get_add_favorite_usecase(repo=Depends(get_favorite_repository)):
    return AddFavoriteUseCase(repo)

from modules.favorites.application.use_cases.remove_favorite import RemoveFavoriteUseCase

def get_remove_favorite_usecase(repo=Depends(get_favorite_repository)):
    return RemoveFavoriteUseCase(repo)


from modules.favorites.application.use_cases.get_favorites import GetFavoritesUseCase

def get_favorites_usecase(repo=Depends(get_favorite_repository)):
    return GetFavoritesUseCase(repo)