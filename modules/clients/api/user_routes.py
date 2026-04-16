from fastapi import APIRouter, Depends, HTTPException
from modules.clients.infrastructure.repositories.user_repository_sql import UserRepositorySQL
from modules.clients.application.use_cases.register_user import RegisterUser

from modules.clients.api.schemas import RegisterRequest, RegisterResponse


router = APIRouter()

def get_user_repo():
    return UserRepositorySQL()

@router.post("/register", response_model=RegisterResponse)
def register(
    data: RegisterRequest,
    repo=Depends(get_user_repo)
):

    use_case = RegisterUser(repo)

    try:
        result = use_case.execute(data.model_dump())
        return result

    except Exception as e:

        if str(e) == "EMAIL_ALREADY_EXISTS":
            raise HTTPException(400, "Email déjà utilisé")

        if str(e) == "CGU_NOT_ACCEPTED":
            raise HTTPException(400, "CGU non acceptées")

        raise HTTPException(500, "Erreur interne")