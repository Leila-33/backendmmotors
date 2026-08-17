from dataclasses import dataclass
from pydantic import EmailStr

@dataclass
class RegisterDTO:
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    accepted_cgu: bool