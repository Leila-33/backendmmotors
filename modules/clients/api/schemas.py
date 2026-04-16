from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class RegisterRequest(BaseModel):
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)
    email: EmailStr
    password: str
    accepted_cgu: bool

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'

        if not re.match(pattern, value):
            raise ValueError(
                "Le mot de passe doit contenir au moins 8 caractères, "
                "une majuscule, une minuscule, un chiffre et un caractère spécial"
            )
        return value


class RegisterResponse(BaseModel):
    id: str
    message: str