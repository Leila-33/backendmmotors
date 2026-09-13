from types import SimpleNamespace
from unittest.mock import Mock, patch
from datetime import datetime, timezone
import pytest

from modules.favorites.application.dtos.add_favorite_dto import (
    AddFavoriteDTO,
)
from modules.favorites.application.results.add_favorite_result import (
    AddFavoriteResult,
)
from modules.favorites.application.use_cases.add_favorite import (
    AddFavoriteUseCase,
)
from modules.favorites.domain.entities.favorite import Favorite
from modules.favorites.domain.exceptions import (
    FavoriteAlreadyExists,
)
from modules.vehicles.domain.exceptions import (
    VehicleNotFound,
)


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def vehicle_repository():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    repository,
    vehicle_repository,
    unit_of_work,
):
    return AddFavoriteUseCase(
        repository=repository,
        vehicle_repository=vehicle_repository,
        unit_of_work=unit_of_work,
    )


@pytest.fixture
def dto():
    return AddFavoriteDTO(
        user_id="user-123",
        vehicle_id="vehicle-123",
    )


@pytest.fixture
def vehicle():
    return SimpleNamespace(
        id="vehicle-123",
    )


def test_execute_creates_favorite_successfully(
    use_case,
    dto,
    vehicle,
    repository,
    vehicle_repository,
    unit_of_work,
):
    vehicle_repository.get_by_id.return_value = vehicle
    repository.exists.return_value = False

    saved_favorite = Favorite(
        id="favorite-123",
        user_id=dto.user_id,
        vehicle_id=dto.vehicle_id,
        created_at=datetime.now(timezone.utc),

    )

    repository.add.return_value = saved_favorite

    result = use_case.execute(dto)

    vehicle_repository.get_by_id.assert_called_once_with(
        dto.vehicle_id,
    )

    repository.exists.assert_called_once_with(
        user_id=dto.user_id,
        vehicle_id=dto.vehicle_id,
    )

    repository.add.assert_called_once()

    favorite_arg = repository.add.call_args.args[0]

    assert isinstance(favorite_arg, Favorite)
    assert favorite_arg.user_id == dto.user_id
    assert favorite_arg.vehicle_id == dto.vehicle_id
    assert favorite_arg.id
    assert favorite_arg.created_at is not None
    assert favorite_arg.created_at.tzinfo is not None

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()

    assert isinstance(result, AddFavoriteResult)
    assert result.id == "favorite-123"


def test_execute_raises_when_vehicle_does_not_exist(
    use_case,
    dto,
    vehicle_repository,
    repository,
    unit_of_work,
):
    vehicle_repository.get_by_id.return_value = None

    with pytest.raises(VehicleNotFound):
        use_case.execute(dto)

    vehicle_repository.get_by_id.assert_called_once_with(
        dto.vehicle_id,
    )

    repository.exists.assert_not_called()
    repository.add.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_execute_raises_when_favorite_already_exists(
    use_case,
    dto,
    vehicle,
    vehicle_repository,
    repository,
    unit_of_work,
):
    vehicle_repository.get_by_id.return_value = vehicle
    repository.exists.return_value = True

    with pytest.raises(FavoriteAlreadyExists):
        use_case.execute(dto)

    vehicle_repository.get_by_id.assert_called_once_with(
        dto.vehicle_id,
    )

    repository.exists.assert_called_once_with(
        user_id=dto.user_id,
        vehicle_id=dto.vehicle_id,
    )

    repository.add.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_execute_rolls_back_when_repository_add_fails(
    use_case,
    dto,
    vehicle,
    vehicle_repository,
    repository,
    unit_of_work,
):
    vehicle_repository.get_by_id.return_value = vehicle
    repository.exists.return_value = False

    repository.add.side_effect = RuntimeError(
        "Database error"
    )

    with pytest.raises(RuntimeError, match="Database error"):
        use_case.execute(dto)

    repository.add.assert_called_once()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_execute_rolls_back_when_commit_fails(
    use_case,
    dto,
    vehicle,
    vehicle_repository,
    repository,
    unit_of_work,
):
    vehicle_repository.get_by_id.return_value = vehicle
    repository.exists.return_value = False

    repository.add.return_value = Favorite(
        id="favorite-123",
        user_id=dto.user_id,
        vehicle_id=dto.vehicle_id,
        created_at=datetime.now(timezone.utc),
    )

    unit_of_work.commit.side_effect = RuntimeError(
        "Commit error"
    )

    with pytest.raises(RuntimeError, match="Commit error"):
        use_case.execute(dto)

    repository.add.assert_called_once()

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()