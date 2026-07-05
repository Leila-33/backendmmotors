from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from modules.core.enums import UserRole
from datetime import datetime

# =========================
# REGISTER
# =========================
class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)
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
    
    @field_validator("accepted_cgu")
    @classmethod
    def validate_cgu(cls, value: bool):
        if value is not True:
            raise ValueError("Vous devez accepter les CGU pour vous inscrire")
        return value


class RegisterResponse(BaseModel):
    message: str


# =========================
# LOGIN
# =========================
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str


# =========================
# REFRESH
# =========================
class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str


# =========================
# VERIFY EMAIL
# =========================
class VerifyEmailRequest(BaseModel):
    token: str


# =========================
# LOGOUT
# =========================
class LogoutRequest(BaseModel):
    token: str


# =========================
# ME
# =========================
class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    is_verified: bool
    first_name: str
    last_name: str


# dto/get_users_dto.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class FindUsersQuery(BaseModel):
    page: int = 1
    limit: int = 10
    search: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None  # all | active | inactive
    sort: Optional[str] = "created_at_desc"

class UserItemDTO(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    role: str
    is_active: bool
    is_deleted: bool
    created_at: Optional[datetime]


class PaginatedUsersResponse(BaseModel):
    items: List[UserItemDTO]
    page: int
    limit: int
    total: int
    pages: int

# dto/get_users_response.py

from typing import List

from datetime import datetime




class UpdateUserRoleSchema(BaseModel):
    role: UserRole



class CreateUserSchema(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    role: UserRole




class ToggleActiveSchema(BaseModel):
    is_active: bool




class ToggleUserActiveResponse(BaseModel):
    id: str
    is_active: bool

class ArchiveUserResponse(BaseModel):
    message: str


class ArchiveUsersSchema(BaseModel):
    ids: List[str]

class ArchiveUsersResponse(BaseModel):
    archived_count: int
    user_ids: List[str]
    message: str