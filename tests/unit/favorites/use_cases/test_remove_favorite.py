from unittest.mock import Mock

import pytest

from modules.favorites.application.dtos.remove_favorite_dto import (
    RemoveFavoriteDTO,
)
from modules.favorites.application.results.remove_favorite_result import (
    RemoveFavoriteResult,
)
from modules.favorites.application.use_cases.remove_favorite import (
    RemoveFavoriteUseCase,
)
from modules.favorites.domain.exceptions import FavoriteNotFound


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(repository, unit_of_work):
    return RemoveFavoriteUseCase(
        repository=repository,
        unit_of_work=unit_of_work,
    )


@pytest.fixture
def dto():
    return RemoveFavoriteDTO(
        user_id="user-123",
        vehicle_id="vehicle-123",
    )


def test_execute_removes_favorite_successfully(
    use_case,
    repository,
    unit_of_work,
    dto,
):
    repository.exists.return_value = True

    result = use_case.execute(dto)

    repository.exists.assert_called_once_with(
        user_id=dto.user_id,
        vehicle_id=dto.vehicle_id,
    )

    repository.delete.assert_called_once_with(
        user_id=dto.user_id,
        vehicle_id=dto.vehicle_id,
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()

    assert isinstance(result, RemoveFavoriteResult)
    assert result.message == "Favori supprimé avec succès."


def test_execute_raises_when_favorite_does_not_exist(
    use_case,
    repository,
    unit_of_work,
    dto,
):
    repository.exists.return_value = False

    with pytest.raises(FavoriteNotFound):
        use_case.execute(dto)

    repository.exists.assert_called_once_with(
        user_id=dto.user_id,
        vehicle_id=dto.vehicle_id,
    )

    repository.delete.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_execute_rolls_back_when_delete_fails(
    use_case,
    repository,
    unit_of_work,
    dto,
):
    repository.exists.return_value = True
    repository.delete.side_effect = RuntimeError("Database error")

    with pytest.raises(
        RuntimeError,
        match="Database error",
    ):
        use_case.execute(dto)

    repository.exists.assert_called_once_with(
        user_id=dto.user_id,
        vehicle_id=dto.vehicle_id,
    )

    repository.delete.assert_called_once_with(
        user_id=dto.user_id,
        vehicle_id=dto.vehicle_id,
    )

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_execute_rolls_back_when_commit_fails(
    use_case,
    repository,
    unit_of_work,
    dto,
):
    repository.exists.return_value = True
    unit_of_work.commit.side_effect = RuntimeError("Commit error")

    with pytest.raises(
        RuntimeError,
        match="Commit error",
    ):
        use_case.execute(dto)

    repository.exists.assert_called_once_with(
        user_id=dto.user_id,
        vehicle_id=dto.vehicle_id,
    )

    repository.delete.assert_called_once_with(
        user_id=dto.user_id,
        vehicle_id=dto.vehicle_id,
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()