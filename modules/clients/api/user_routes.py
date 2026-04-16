from fastapi import APIRouter, Depends, HTTPException
from modules.clients.infrastructure.repositories.user_repository_sql import UserRepositorySQL
from modules.clients.application.use_cases.register_user import RegisterUser

from modules.clients.api.schemas import RegisterRequest, RegisterResponse


router = APIRouter()


@router.post("/register", response_model=RegisterResponse)
def register(data: RegisterRequest):

    repo = UserRepositorySQL()
    use_case = RegisterUser(repo)

    try:
        return use_case.execute(data.model_dump())

    except Exception as e:

        if str(e) == "EMAIL_ALREADY_EXISTS":
            raise HTTPException(
                status_code=400,
                detail="Cet email est déjà utilisé"
            )

        if str(e) == "CGU_NOT_ACCEPTED":
            raise HTTPException(
                status_code=400,
                detail="Vous devez accepter les CGU"
            )

        raise HTTPException(
            status_code=500,
            detail="Erreur interne"
        )