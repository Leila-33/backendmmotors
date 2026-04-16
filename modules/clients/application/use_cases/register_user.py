import uuid
from modules.clients.domain.entities.user import User
from shared.security import hash_password


class RegisterUser:

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def execute(self, data: dict):

        # 🔹 1. Vérifier email unique
        existing_user = self.user_repository.get_by_email(data["email"])
        if existing_user:
            raise Exception("EMAIL_ALREADY_EXISTS")

        # 🔹 2. Vérifier CGU (règle métier)
        if not data["accepted_cgu"]:
            raise Exception("CGU_NOT_ACCEPTED")

        # 🔹 3. Hash du mot de passe
        hashed_password = hash_password(data["password"])

        # 🔹 4. Création de l'utilisateur
        user = User(
            id=str(uuid.uuid4()),
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            password=hashed_password,
            accepted_cgu=data["accepted_cgu"]
        )

        # 🔹 5. Sauvegarde
        self.user_repository.save(user)

        # 🔹 6. Réponse
        return {
            "message": "Compte créé avec succès"
        }