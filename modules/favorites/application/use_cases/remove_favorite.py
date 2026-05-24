from modules.core.exceptions import FavoriteNotFound

class RemoveFavoriteUseCase:

    def __init__(self, repo):
        self.repo = repo

    def execute(self, user_id, vehicle_id):

        if not self.repo.exists(user_id, vehicle_id):
            raise FavoriteNotFound()

        self.repo.delete(user_id, vehicle_id)
        self.repo.commit()