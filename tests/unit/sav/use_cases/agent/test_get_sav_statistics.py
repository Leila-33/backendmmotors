from unittest.mock import Mock

import pytest

from modules.sav.application.results.agent.get_sav_statistics_result import (
    GetSavStatisticsResult,
    CategoryStatResult,
)
from modules.sav.application.use_cases.agent.get_sav_statistics import (
    GetSavStatisticsUseCase,
)


# ============================================================
# HELPERS
# ============================================================


def make_statistics_data(
    *,
    total: int = 20,
    closed: int = 12,
    last_7_days: int = 5,
    last_30_days: int = 14,
    category_distribution=None,
    resolution_rate: float = 60.0,
):
    return {
        "total": total,
        "closed": closed,
        "last_7_days": last_7_days,
        "last_30_days": last_30_days,
        "category_distribution": (
            []
            if category_distribution is None
            else category_distribution
        ),
        "resolution_rate": resolution_rate,
    }


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def repo():
    return Mock()


@pytest.fixture
def use_case(repo):
    return GetSavStatisticsUseCase(
        repo=repo
    )


@pytest.fixture
def user_id():
    return "agent-123"


# ============================================================
# REPOSITORY
# ============================================================


def test_execute_calls_repository_with_user_id(
    use_case,
    repo,
    user_id,
):
    repo.get_sav_statistics.return_value = (
        make_statistics_data()
    )

    use_case.execute(
        user_id=user_id
    )

    repo.get_sav_statistics.assert_called_once_with(
        user_id
    )


# ============================================================
# RESULT
# ============================================================


def test_execute_returns_get_sav_statistics_result(
    use_case,
    repo,
    user_id,
):
    repo.get_sav_statistics.return_value = (
        make_statistics_data()
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert isinstance(
        result,
        GetSavStatisticsResult,
    )


# ============================================================
# COUNTERS
# ============================================================


def test_execute_returns_total(
    use_case,
    repo,
    user_id,
):
    repo.get_sav_statistics.return_value = (
        make_statistics_data(
            total=42
        )
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert result.total == 42


def test_execute_returns_closed(
    use_case,
    repo,
    user_id,
):
    repo.get_sav_statistics.return_value = (
        make_statistics_data(
            closed=27
        )
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert result.closed == 27


def test_execute_returns_last_7_days(
    use_case,
    repo,
    user_id,
):
    repo.get_sav_statistics.return_value = (
        make_statistics_data(
            last_7_days=8
        )
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert result.last_7_days == 8


def test_execute_returns_last_30_days(
    use_case,
    repo,
    user_id,
):
    repo.get_sav_statistics.return_value = (
        make_statistics_data(
            last_30_days=19
        )
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert result.last_30_days == 19


def test_execute_returns_resolution_rate(
    use_case,
    repo,
    user_id,
):
    repo.get_sav_statistics.return_value = (
        make_statistics_data(
            resolution_rate=87.5
        )
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert result.resolution_rate == 87.5


@pytest.mark.parametrize(
    "total,closed,last_7_days,last_30_days,resolution_rate",
    [
        (0, 0, 0, 0, 0.0),
        (10, 5, 2, 7, 50.0),
        (100, 80, 15, 60, 80.0),
        (250, 125, 25, 100, 50.0),
    ],
)
def test_execute_preserves_statistics(
    total,
    closed,
    last_7_days,
    last_30_days,
    resolution_rate,
    use_case,
    repo,
    user_id,
):
    repo.get_sav_statistics.return_value = (
        make_statistics_data(
            total=total,
            closed=closed,
            last_7_days=last_7_days,
            last_30_days=last_30_days,
            resolution_rate=resolution_rate,
        )
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert result.total == total
    assert result.closed == closed
    assert result.last_7_days == last_7_days
    assert result.last_30_days == last_30_days
    assert result.resolution_rate == resolution_rate


# ============================================================
# CATEGORY DISTRIBUTION
# ============================================================


def test_execute_returns_empty_category_distribution(
    use_case,
    repo,
    user_id,
):
    repo.get_sav_statistics.return_value = (
        make_statistics_data(
            category_distribution=[]
        )
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert result.category_distribution == []


def test_execute_transforms_category_distribution(
    use_case,
    repo,
    user_id,
):
    repo.get_sav_statistics.return_value = (
        make_statistics_data(
            category_distribution=[
                ("WARRANTY", 5),
                ("PAYMENT", 3),
                ("DELIVERY", 2),
            ]
        )
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert len(
        result.category_distribution
    ) == 3

    assert all(
        isinstance(
            item,
            CategoryStatResult,
        )
        for item in result.category_distribution
    )

    assert (
        result.category_distribution[0].category
        == "WARRANTY"
    )
    assert (
        result.category_distribution[0].count
        == 5
    )

    assert (
        result.category_distribution[1].category
        == "PAYMENT"
    )
    assert (
        result.category_distribution[1].count
        == 3
    )

    assert (
        result.category_distribution[2].category
        == "DELIVERY"
    )
    assert (
        result.category_distribution[2].count
        == 2
    )


def test_execute_preserves_category_order(
    use_case,
    repo,
    user_id,
):
    categories = [
        ("GENERAL", 10),
        ("FINANCING", 7),
        ("VEHICLE_ISSUE", 4),
        ("DOCUMENTS", 2),
    ]

    repo.get_sav_statistics.return_value = (
        make_statistics_data(
            category_distribution=categories
        )
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert [
        item.category
        for item in result.category_distribution
    ] == [
        "GENERAL",
        "FINANCING",
        "VEHICLE_ISSUE",
        "DOCUMENTS",
    ]

    assert [
        item.count
        for item in result.category_distribution
    ] == [
        10,
        7,
        4,
        2,
    ]


def test_execute_handles_zero_category_count(
    use_case,
    repo,
    user_id,
):
    repo.get_sav_statistics.return_value = (
        make_statistics_data(
            category_distribution=[
                ("GENERAL", 0),
                ("OTHER", 0),
            ]
        )
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert len(
        result.category_distribution
    ) == 2

    assert (
        result.category_distribution[0].count
        == 0
    )

    assert (
        result.category_distribution[1].count
        == 0
    )


# ============================================================
# COMPLETE RESULT
# ============================================================


def test_execute_returns_complete_statistics(
    use_case,
    repo,
    user_id,
):
    repo.get_sav_statistics.return_value = (
        make_statistics_data(
            total=50,
            closed=35,
            last_7_days=6,
            last_30_days=22,
            category_distribution=[
                ("WARRANTY", 15),
                ("PAYMENT", 10),
                ("DELIVERY", 5),
            ],
            resolution_rate=70.0,
        )
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert isinstance(
        result,
        GetSavStatisticsResult,
    )

    assert result.total == 50
    assert result.closed == 35
    assert result.last_7_days == 6
    assert result.last_30_days == 22
    assert result.resolution_rate == 70.0

    assert len(
        result.category_distribution
    ) == 3

    assert (
        result.category_distribution[0].category
        == "WARRANTY"
    )
    assert (
        result.category_distribution[0].count
        == 15
    )

    assert (
        result.category_distribution[1].category
        == "PAYMENT"
    )
    assert (
        result.category_distribution[1].count
        == 10
    )

    assert (
        result.category_distribution[2].category
        == "DELIVERY"
    )
    assert (
        result.category_distribution[2].count
        == 5
    )


# ============================================================
# ERROR
# ============================================================


def test_repository_error_is_propagated(
    use_case,
    repo,
    user_id,
):
    repo.get_sav_statistics.side_effect = RuntimeError(
        "statistics repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="statistics repository error",
    ):
        use_case.execute(
            user_id=user_id
        )

    repo.get_sav_statistics.assert_called_once_with(
        user_id
    )


# ============================================================
# NO UNEXPECTED OPERATIONS
# ============================================================


def test_execute_only_reads_statistics(
    use_case,
    repo,
    user_id,
):
    repo.get_sav_statistics.return_value = (
        make_statistics_data()
    )

    use_case.execute(
        user_id=user_id
    )

    repo.get_sav_statistics.assert_called_once_with(
        user_id
    )

    repo.create.assert_not_called()
    repo.update.assert_not_called()
    repo.delete.assert_not_called()
