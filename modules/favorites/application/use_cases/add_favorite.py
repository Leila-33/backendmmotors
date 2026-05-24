from uuid import uuid4
from modules.core.exceptions import FavoriteAlreadyExists
from modules.favorites.infrastructure.db.favorite_model import FavoriteModel

class AddFavoriteUseCase:

    def __init__(self, repo):
        self.repo = repo

    def execute(self, user_id, vehicle_id):

        if self.repo.exists(user_id, vehicle_id):
            raise FavoriteAlreadyExists()

        favorite = FavoriteModel(
            id=str(uuid4()),
            user_id=user_id,
            vehicle_id=vehicle_id
        )

        self.repo.add(favorite)
        self.repo.commit()

        return favorite