from modules.auth.application.results.admin.user_list_item_result import (
    UserListItemResult,
)
from modules.auth.application.dtos.admin.find_users_dto import (
    FindUsersDTO,
)
from core.pagination.paginated_result import PaginatedResult

class FindUsersUseCase:
    """
    Récupère les utilisateurs selon les critères de recherche,
    de filtrage, de tri et de pagination, puis transforme les
    résultats en données adaptées à la liste d'administration.
    """
    def __init__(
        self,
        user_repo,
    ):
        self.user_repo = user_repo

    def execute(
        self,
        dto : FindUsersDTO,
    ) -> PaginatedResult[UserListItemResult]:

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

        return PaginatedResult.create(
            items=items,
            page=dto.page,
            limit=dto.limit,
            total=total,
        )