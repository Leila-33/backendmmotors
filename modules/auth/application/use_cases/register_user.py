import uuid
from core.security.password import hash_password
from modules.core.exceptions import EmailAlreadyExists
from modules.auth.domain.entities.user import User


class RegisterUser:

    def __init__(self, user_repo, jwt_service, email_service):
        self.user_repo = user_repo
        self.jwt = jwt_service
        self.email_service = email_service

    def execute(self, data):

        if self.user_repo.get_by_email(data.email):
            raise EmailAlreadyExists()

        user = User(
            id=str(uuid.uuid4()),
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            password=hash_password(data.password),
            role="client",
            is_verified=False,
            is_active=True,
            accepted_cgu=True
        )

        self.user_repo.save(user)

        token = self.jwt.create_email_token(user.id)

        self.email_service.send_verification_email(
            email=user.email,
            token=token
        )

        return {"message": "User created"}