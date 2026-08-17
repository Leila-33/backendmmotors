from dataclasses import dataclass


@dataclass
class ArchiveUsersResult:
    archived_count: int
    user_ids: list[str]