class DeleteOption:

    def __init__(self, repo):
        self.repo = repo

    def execute(self, option_id: str):
        self.repo.delete(option_id)
        return {"message": "Option désactivée"}