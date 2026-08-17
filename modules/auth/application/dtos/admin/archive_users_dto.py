from dataclasses import dataclass


@dataclass
class ArchiveUsersDTO:

    user_ids: list[str]