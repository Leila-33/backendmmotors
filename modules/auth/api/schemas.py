from datetime import datetime

import re

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)

from modules.auth.domain.enums import (
    UserRole,
    UserStatusFilter
)


# =========================================================
# CLIENT
# =========================================================

# =========================
# REGISTER
# =========================

class RegisterRequest(BaseModel):

    first_name: str = Field(
        min_length=2,
        max_length=50,
    )

    last_name: str = Field(
        min_length=2,
        max_length=50,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=100,
    )

    accepted_cgu: bool

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):

        pattern = (
            r"^(?=.*[a-z])"
            r"(?=.*[A-Z])"
            r"(?=.*\d)"
            r"(?=.*[@$!%*?&]).{8,}$"
        )

        if not re.match(pattern, value):
            raise ValueError(
                "Le mot de passe doit contenir au moins 8 caractères, "
                "une majuscule, une minuscule, un chiffre "
                "et un caractère spécial"
            )

        return value

    @field_validator("accepted_cgu")
    @classmethod
    def validate_cgu(cls, value: bool):

        if value is not True:
            raise ValueError(
                "Vous devez accepter les CGU pour vous inscrire"
            )

        return value


class RegisterResponse(BaseModel):
    message: str


# =========================
# LOGIN
# =========================

class LoginUserRequest(BaseModel):

    email: EmailStr

    password: str


class LoginUserResponse(BaseModel):

    access_token: str


# =========================
# REFRESH
# =========================

class RefreshTokenResponse(BaseModel):

    access_token: str


# =========================
# VERIFY EMAIL
# =========================

class VerifyEmailResponse(BaseModel):

    message: str


# =========================
# LOGOUT
# =========================

class LogoutResponse(BaseModel):

    message: str


# =========================
# ME
# =========================

class UserResponse(BaseModel):

    id: str

    email: str

    role: UserRole

    is_verified: bool

    first_name: str

    last_name: str


# =========================
# CHECK ACTIVATION TOKEN
# =========================

class CheckActivationTokenResponse(BaseModel):

    first_name: str

    email: str

    already_verified: bool

    expired: bool


# =========================
# ACTIVATE ACCOUNT
# =========================

class ActivateAccountRequest(BaseModel):

    token: str

    password: str = Field(
        min_length=8,
        max_length=100,
    )

    accepted_cgu: bool

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):

        pattern = (
            r"^(?=.*[a-z])"
            r"(?=.*[A-Z])"
            r"(?=.*\d)"
            r"(?=.*[@$!%*?&]).{8,}$"
        )

        if not re.match(pattern, value):
            raise ValueError(
                "Le mot de passe doit contenir au moins 8 caractères, "
                "une majuscule, une minuscule, un chiffre "
                "et un caractère spécial"
            )

        return value

    @field_validator("accepted_cgu")
    @classmethod
    def validate_cgu(cls, value: bool):

        if value is not True:
            raise ValueError(
                "Vous devez accepter les CGU pour activer votre compte"
            )

        return value


class ActivateAccountResponse(BaseModel):

    message: str

    access_token: str

    redirect: str


# =========================================================
# ADMIN
# =========================================================

# =========================
# FIND USERS
# =========================

class FindUsersRequest(BaseModel):

    page: int = Field(
        default=1,
        ge=1,
    )

    limit: int = Field(
        default=10,
        ge=1,
        le=100,
    )

    search: str | None = None

    role: UserRole | None = None

    status: UserStatusFilter | None = None

    sort: str = "created_at_desc"


class UserItemResponse(BaseModel):

    id: str

    first_name: str

    last_name: str

    email: str

    role: UserRole

    is_active: bool

    is_deleted: bool

    is_verified: bool

    created_at: datetime


class PaginatedUsersResponse(BaseModel):

    items: list[UserItemResponse]

    page: int

    limit: int

    total: int

    pages: int


# =========================
# UPDATE USER ROLE
# =========================

class UpdateUserRoleRequest(BaseModel):

    role: UserRole


class UpdateUserRoleResponse(BaseModel):

    id: str

    role: UserRole

    message: str


# =========================
# TOGGLE ACTIVE
# =========================

class ToggleUserActiveRequest(BaseModel):

    is_active: bool


class ToggleUserActiveResponse(BaseModel):

    id: str

    is_active: bool

    message: str


# =========================
# ARCHIVE USER
# =========================

class ArchiveUserResponse(BaseModel):

    id: str

    message: str


# =========================
# ARCHIVE USERS
# =========================

class ArchiveUsersRequest(BaseModel):

    user_ids: list[str]


class ArchiveUsersResponse(BaseModel):

    archived_count: int

    user_ids: list[str]

    message: str


# =========================
# CREATE USER
# =========================

class CreateUserRequest(BaseModel):

    first_name: str = Field(
        min_length=2,
        max_length=50,
    )

    last_name: str = Field(
        min_length=2,
        max_length=50,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=100,
    )

    role: UserRole

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):

        pattern = (
            r"^(?=.*[a-z])"
            r"(?=.*[A-Z])"
            r"(?=.*\d)"
            r"(?=.*[@$!%*?&]).{8,}$"
        )

        if not re.match(pattern, value):
            raise ValueError(
                "Le mot de passe doit contenir au moins 8 caractères, "
                "une majuscule, une minuscule, un chiffre "
                "et un caractère spécial"
            )

        return value


class CreateUserResponse(BaseModel):

    id: str

    email: EmailStr

    role: UserRole

    message: str


# find users

class FindUsersRequest(BaseModel):

    page: int = Field(
        default=1,
        ge=1,
    )

    limit: int = Field(
        default=10,
        ge=1,
        le=100,
    )

    search: str | None = None

    role: str | None = None

    status: str | None = None

    sort: str = "created_at_desc"













