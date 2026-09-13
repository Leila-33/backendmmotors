from types import SimpleNamespace

import pytest

from modules.inspections.domain.entities.inspection_result import (
    InspectionResult,
)
from modules.inspections.domain.services.inspection_engine import (
    InspectionEngine,
)


@pytest.fixture
def engine():
    return InspectionEngine()


def test_run_returns_expected_inspection_result(engine):
    vehicle = SimpleNamespace(
        mileage=50000,
        year=2020,
    )

    result = engine.run(vehicle)

    assert isinstance(result, InspectionResult)

    assert result.engine_score == 80
    assert result.brakes_score == 85
    assert result.tires_score == 80
    assert result.electronics_score == 90

    assert result.safety_score == 82
    assert result.overall_score == 83

    assert result.failures == []
    assert result.recommended_repairs == []


def test_run_detects_engine_failure(engine):
    vehicle = SimpleNamespace(
        mileage=160000,
        year=2020,
    )

    result = engine.run(vehicle)

    # 80 - 20 = 60
    # 60 n'est pas inférieur à 60 : aucune panne moteur.
    assert result.engine_score == 60
    assert "ENGINE_LOW" not in result.failures
    assert "ENGINE_DIAG" not in result.recommended_repairs


def test_run_detects_engine_failure_for_old_vehicle(engine):
    vehicle = SimpleNamespace(
        mileage=50000,
        year=2010,
    )

    result = engine.run(vehicle)

    # 80 - 15 = 65
    # Pas de panne car 65 >= 60.
    assert result.engine_score == 65
    assert "ENGINE_LOW" not in result.failures

    vehicle.year = 2000

    result = engine.run(vehicle)

    # 80 - 15 = 65 également.
    assert result.engine_score == 65


def test_run_detects_brakes_and_tires_failures(engine):
    vehicle = SimpleNamespace(
        mileage=130000,
        year=2020,
    )

    result = engine.run(vehicle)

    # Freins : 85 - 25 = 60
    assert result.brakes_score == 60
    assert "BRAKES_WORN" not in result.failures

    # Pneus : 80 - 30 = 50
    assert result.tires_score == 50
    assert "TIRES_WORN" not in result.failures

    vehicle.mileage = 150000

    result = engine.run(vehicle)

    # Les scores restent plafonnés à ces valeurs :
    # freins = 60, pneus = 50
    assert result.brakes_score == 60
    assert result.tires_score == 50


def test_run_detects_electronics_failure_for_old_vehicle(engine):
    vehicle = SimpleNamespace(
        mileage=50000,
        year=2010,
    )

    result = engine.run(vehicle)

    # 90 - 20 = 70
    assert result.electronics_score == 70
    assert "ELECTRONICS_FAULT" not in result.failures

    vehicle.year = 2014

    result = engine.run(vehicle)

    assert result.electronics_score == 70
    assert "ELECTRONICS_FAULT" not in result.failures


def test_run_detects_multiple_failures_and_repairs(engine):
    vehicle = SimpleNamespace(
        mileage=200000,
        year=2010,
    )

    result = engine.run(vehicle)

    assert result.engine_score == 45
    assert result.brakes_score == 60
    assert result.tires_score == 50
    assert result.electronics_score == 70

    assert result.failures == [
        "ENGINE_LOW",
    ]

    assert result.recommended_repairs == [
        "ENGINE_DIAG",
    ]


def test_run_calculates_safety_and_overall_scores(engine):
    vehicle = SimpleNamespace(
        mileage=200000,
        year=2010,
    )

    result = engine.run(vehicle)

    expected_safety_score = int(
        (result.brakes_score + result.tires_score) / 2
    )

    expected_overall_score = int(
        (
            result.engine_score
            + result.brakes_score
            + result.tires_score
            + result.electronics_score
        ) / 4
    )

    assert result.safety_score == expected_safety_score
    assert result.overall_score == expected_overall_score