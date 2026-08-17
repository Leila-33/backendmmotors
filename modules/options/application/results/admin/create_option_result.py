from dataclasses import dataclass


@dataclass
class CreateOptionResult:

    option_id: str
    message: str