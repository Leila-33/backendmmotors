from math import ceil

from modules.auth.application.results.admin.find_users_result import (
    FindUsersResult,
    UserListItemResult,
)
from modules.auth.application.dtos.admin.find_users_dto import (
    FindUsersDTO,
)

class FindUsersUseCase:

    def __init__(
        self,
        user_repo,
    ):
        self.user_repo = user_repo

    def execute(
        self,
        dto : FindUsersDTO,
    ) -> FindUsersResult:

        users, total = self.user_repo.find_all(
            page=dto.page,
            limit=dto.limit,
            search=dto.search,
            role=dto.role,
            status=dto.status,
            sort=dto.sort,
        )

        items = [
            UserListItemResult(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                is_deleted=user.is_deleted,
                is_verified=user.is_verified,
                created_at=user.created_at,
            )
            for user in users
        ]

        pages = (
            ceil(total / dto.limit)
            if dto.limit
            else 1
        )

        return FindUsersResult(
            items=items,
            page=dto.page,
            limit=dto.limit,
            total=total,
            pages=pages,
        )