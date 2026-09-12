from datetime import datetime, timezone
from unittest.mock import Mock


from modules.auth.application.use_cases.admin.find_users import (
    FindUsersUseCase,
)
from modules.auth.application.dtos.admin.find_users_dto import (
    FindUsersDTO,
)
from modules.auth.domain.entities.user import User
from modules.auth.domain.enums import UserRole


def create_user(
    user_id: str,
    first_name: str = "Leila",
    last_name: str = "El",
    email: str = "leila.el@example.com",
    role: UserRole = UserRole.CLIENT,
) -> User:
    return User(
        id=user_id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password="hashed-password",
        role=role,
        is_verified=True,
        is_active=True,
        accepted_cgu=True,
        is_deleted=False,
        deleted_at=None,
        created_at=datetime.now(timezone.utc),
    )


def create_dto(
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
    role: UserRole | None = None,
    status: str | None = None,
    sort: str | None = None,
) -> FindUsersDTO:
    return FindUsersDTO(
        page=page,
        limit=limit,
        search=search,
        role=role,
        status=status,
        sort=sort,
    )


def test_find_users_success():
    user_repo = Mock()

    user1 = create_user(
        user_id="user-1",
        first_name="Leila",
        last_name="El",
        email="leila.el@example.com",
    )

    user2 = create_user(
        user_id="user-2",
        first_name="Marie",
        last_name="Martin",
        email="marie@example.com",
        role=UserRole.CLIENT,
    )

    user_repo.find_all.return_value = (
        [user1, user2],
        2,
    )

    dto = create_dto(
        page=1,
        limit=10,
    )

    use_case = FindUsersUseCase(
        user_repo=user_repo,
    )

    result = use_case.execute(dto)

    # -------------------------------------------------
    # Résultat général
    # -------------------------------------------------

    assert result.page == 1
    assert result.limit == 10
    assert result.total == 2
    assert result.pages == 1

    # -------------------------------------------------
    # Items
    # -------------------------------------------------

    assert len(result.items) == 2

    item1 = result.items[0]

    assert item1.id == "user-1"
    assert item1.first_name == "Leila"
    assert item1.last_name == "El"
    assert item1.email == "leila.el@example.com"
    assert item1.role == UserRole.CLIENT
    assert item1.is_active is True
    assert item1.is_deleted is False
    assert item1.is_verified is True
    assert item1.created_at == user1.created_at

    item2 = result.items[1]

    assert item2.id == "user-2"
    assert item2.first_name == "Marie"
    assert item2.last_name == "Martin"
    assert item2.email == "marie@example.com"

    # -------------------------------------------------
    # Repository
    # -------------------------------------------------

    user_repo.find_all.assert_called_once_with(
        page=1,
        limit=10,
        search=None,
        role=None,
        status=None,
        sort=None,
    )


def test_find_users_passes_filters_to_repository():
    user_repo = Mock()

    user = create_user("user-1")

    user_repo.find_all.return_value = (
        [user],
        1,
    )

    dto = create_dto(
        page=2,
        limit=5,
        search="Leila",
        role=UserRole.CLIENT,
        status="active",
        sort="created_at_desc",
    )

    use_case = FindUsersUseCase(
        user_repo=user_repo,
    )

    result = use_case.execute(dto)

    user_repo.find_all.assert_called_once_with(
        page=2,
        limit=5,
        search="Leila",
        role=UserRole.CLIENT,
        status="active",
        sort="created_at_desc",
    )

    assert result.page == 2
    assert result.limit == 5
    assert result.total == 1
    assert result.pages == 1


def test_find_users_calculates_multiple_pages():
    user_repo = Mock()

    users = [
        create_user("user-1"),
        create_user("user-2"),
        create_user("user-3"),
    ]

    # 23 utilisateurs au total
    # 10 utilisateurs par page
    # => ceil(23 / 10) = 3 pages
    user_repo.find_all.return_value = (
        users,
        23,
    )

    dto = create_dto(
        page=2,
        limit=10,
    )

    use_case = FindUsersUseCase(
        user_repo=user_repo,
    )

    result = use_case.execute(dto)

    assert result.page == 2
    assert result.limit == 10
    assert result.total == 23
    assert result.pages == 3

    assert len(result.items) == 3


def test_find_users_empty_result():
    user_repo = Mock()

    user_repo.find_all.return_value = (
        [],
        0,
    )

    dto = create_dto(
        page=1,
        limit=10,
    )

    use_case = FindUsersUseCase(
        user_repo=user_repo,
    )

    result = use_case.execute(dto)

    assert result.items == []
    assert result.page == 1
    assert result.limit == 10
    assert result.total == 0
    assert result.pages == 0

    user_repo.find_all.assert_called_once_with(
        page=1,
        limit=10,
        search=None,
        role=None,
        status=None,
        sort=None,
    )


def test_find_users_with_limit_zero():
    user_repo = Mock()

    user = create_user("user-1")

    user_repo.find_all.return_value = (
        [user],
        1,
    )

    dto = create_dto(
        page=1,
        limit=0,
    )

    use_case = FindUsersUseCase(
        user_repo=user_repo,
    )

    result = use_case.execute(dto)

    assert result.limit == 0
    assert result.total == 1
    assert result.pages == 1

    assert len(result.items) == 1

    user_repo.find_all.assert_called_once_with(
        page=1,
        limit=0,
        search=None,
        role=None,
        status=None,
        sort=None,
    )