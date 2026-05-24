# usecases/get_users_usecase.py

from modules.auth.api.schemas import GetUsersResponseDTO, UserItemDTO


class GetUsersUseCase:

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def execute(self, dto):

        users, total = self.user_repository.find_all(
            page=dto.page,
            limit=dto.limit,
            search=dto.search,
            role=dto.role
        )

        items = [
            UserItemDTO(
                id=u.id,
                first_name=u.first_name,
                last_name=u.last_name,
                email=u.email,
                role=u.role,
            )
            for u in users
        ]

        pages = (total + dto.limit - 1) // dto.limit

        return GetUsersResponseDTO(
            items=items,
            page=dto.page,
            limit=dto.limit,
            total=total,
            pages=pages
        )