from modules.core.exceptions import TokenInvalid


class VerifyEmail:

    def __init__(self, user_repo, jwt_service):
        self.user_repo = user_repo
        self.jwt = jwt_service

    def execute(self, token: str):

        payload = self.jwt.decode(token)

        if payload["type"] != "email_verification":
            raise TokenInvalid()

        user = self.user_repo.get_by_id(payload["sub"])

        if not user:
            raise TokenInvalid()

        user.is_verified = True
        self.user_repo.update(user)

        return {"message": "Email verified"}