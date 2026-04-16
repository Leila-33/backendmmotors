# modules/auth/dependencies.py

from pydantic import BaseModel


class CurrentUser(BaseModel):
    id: str


def get_current_user() -> CurrentUser:
    return CurrentUser(id="test-user-id")