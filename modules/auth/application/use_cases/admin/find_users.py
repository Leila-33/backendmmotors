from math import ceil
from modules.auth.api.schemas import PaginatedUsersResponse, UserItemDTO


class FindUsersUseCase:

    def __init__(self, user_repo):
        self.user_repo = user_repo

    def execute(self, query):

        users, total = self.user_repo.find_all(
            page=query.page,
            limit=query.limit,
            search=query.search,
            role=query.role,
            status=query.status,
            sort=query.sort
        )
     
        items = [
            UserItemDTO(
                id=u.id,
                first_name=u.first_name,
                last_name=u.last_name,
                email=u.email,
                role=u.role,
                is_active=u.is_active,
                is_deleted=u.is_deleted,
                is_verified=u.is_verified,
                created_at=u.created_at
            )
            for u in users
        ]

        return PaginatedUsersResponse(
            items=items,
            page=query.page,
            limit=query.limit,
            total=total,
            pages=ceil(total / query.limit) if query.limit else 1
        )