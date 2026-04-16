from dataclasses import dataclass

@dataclass
class User:
    id: str
    first_name: str
    last_name: str
    email: str
    password: str
    accepted_cgu: bool