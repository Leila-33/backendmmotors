from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from modules.favorites.application.dtos.get_favorites_dto import (
    GetFavoritesDTO,
)
from modules.favorites.application.results.get_favorites_result import (
    GetFavoritesResult,
    FavoriteItemResult,
    FavoriteVehicleResult,
)
from modules.favorites.application.use_cases.get_favorites import (
    GetFavoritesUseCase,
)


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def use_case(repository):
    return GetFavoritesUseCase(repository=repository)


@pytest.fixture
def dto():
    return GetFavoritesDTO(
        user_id="user-123",
    )


def make_favorite(
    favorite_id="favorite-123",
    vehicle_id="vehicle-123",
    created_at=None,
    images=None,
):
    favorite = Mock()

    favorite.id = favorite_id
    favorite.created_at = created_at

    favorite.vehicle = Mock()
    favorite.vehicle.id = vehicle_id
    favorite.vehicle.brand = "Peugeot"
    favorite.vehicle.model = "308"
    favorite.vehicle.year = 2024
    favorite.vehicle.price = 24990.0
    favorite.vehicle.mileage = 15000
    favorite.vehicle.type = "SALE"
    favorite.vehicle.images = images

    return favorite


def test_execute_returns_favorites_with_vehicle_data(
    use_case,
    repository,
    dto,
):
    created_at = datetime(
        2026,
        9,
        1,
        10,
        30,
        tzinfo=timezone.utc,
    )

    favorite = make_favorite(
        created_at=created_at,
        images=["image1.jpg", "image2.jpg"],
    )

    repository.get_user_favorites.return_value = [favorite]

    result = use_case.execute(dto)

    repository.get_user_favorites.assert_called_once_with(
        dto.user_id
    )

    assert isinstance(result, GetFavoritesResult)
    assert len(result.items) == 1

    item = result.items[0]

    assert isinstance(item, FavoriteItemResult)
    assert item.id == "favorite-123"
    assert item.created_at == created_at.isoformat()

    assert isinstance(item.vehicle, FavoriteVehicleResult)
    assert item.vehicle.id == "vehicle-123"
    assert item.vehicle.brand == "Peugeot"
    assert item.vehicle.model == "308"
    assert item.vehicle.year == 2024
    assert item.vehicle.price == 24990.0
    assert item.vehicle.mileage == 15000
    assert item.vehicle.type == "SALE"
    assert item.vehicle.images == [
        "image1.jpg",
        "image2.jpg",
    ]


def test_execute_handles_none_created_at(
    use_case,
    repository,
    dto,
):
    favorite = make_favorite(
        created_at=None,
        images=["image.jpg"],
    )

    repository.get_user_favorites.return_value = [favorite]

    result = use_case.execute(dto)

    item = result.items[0]

    assert item.created_at is None


def test_execute_handles_none_images(
    use_case,
    repository,
    dto,
):
    favorite = make_favorite(
        created_at=datetime(
            2026,
            9,
            1,
            tzinfo=timezone.utc,
        ),
        images=None,
    )

    repository.get_user_favorites.return_value = [favorite]

    result = use_case.execute(dto)

    item = result.items[0]

    assert item.vehicle.images == []


def test_execute_returns_empty_result_when_user_has_no_favorites(
    use_case,
    repository,
    dto,
):
    repository.get_user_favorites.return_value = []

    result = use_case.execute(dto)

    repository.get_user_favorites.assert_called_once_with(
        dto.user_id
    )

    assert isinstance(result, GetFavoritesResult)
    assert result.items == []