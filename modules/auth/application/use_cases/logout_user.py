class LogoutUser:

    def __init__(self, blacklist_repo):
        self.blacklist_repo = blacklist_repo

    def execute(self, token: str):

        self.blacklist_repo.add(token)

        return {"message": "Logged out"}