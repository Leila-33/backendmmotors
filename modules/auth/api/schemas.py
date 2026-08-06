from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from modules.auth.domain.enums import UserRole
from datetime import datetime
from typing import List, Optional

# =========================
# CLIENT
# =========================

# register

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



# login

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str


# refresh

from dataclasses import dataclass


@dataclass(slots=True)
class RefreshTokensResult:

    access_token: str

    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str


# verify email

class VerifyEmailRequest(BaseModel):
    token: str

class VerifyEmailResponse(BaseModel):

    message: str

# logout

class LogoutResponse(BaseModel):

    message: str

# me

class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    is_verified: bool
    first_name: str
    last_name: str

# check activation token

class CheckActivationTokenResponse(BaseModel):

    first_name: str

    email: str

    already_verified: bool

    expired: bool


# activate account

class ActivateAccountRequest(BaseModel):

    token: str

    password: str

    accepted_cgu: bool


class ActivateAccountResponse(BaseModel):

    message: str

    access_token: str

    refresh_token: str

    redirect: str

class ActivateAccountHttpResponse(BaseModel):

    message: str

    access_token: str

    redirect: str






# =========================
# ADMIN
# =========================

# update user role

class UpdateUserRoleResponse(BaseModel):

    id: str

    role: UserRole

    message: str

class UpdateUserRoleRequest(BaseModel):

    role: UserRole


# toggle active

class ToggleUserActiveRequest(BaseModel):

    is_active: bool

class ToggleUserActiveResponse(BaseModel):

    id: str

    is_active: bool

    message: str


# archive user

class ArchiveUserResponse(BaseModel):

    message: str

# archive users

class ArchiveUsersRequest(BaseModel):

    user_ids: list[str]

class ArchiveUsersResponse(BaseModel):

    archived_count: int

    user_ids: list[str]

    message: str

# create user

class CreateUserRequest(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=100
    )    
    role: UserRole

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

class CreateUserResponse(BaseModel):

    id: str

    email: str

    role: UserRole

    message: str


# find users

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
    is_verified: bool
    created_at: Optional[datetime]


class PaginatedUsersResponse(BaseModel):
    items: List[UserItemDTO]
    page: int
    limit: int
    total: int
    pages: int












