from dataclasses import dataclass


@dataclass
class ActivateAccountDTO:
    token: str
    password: str
    accepted_cgu: bool