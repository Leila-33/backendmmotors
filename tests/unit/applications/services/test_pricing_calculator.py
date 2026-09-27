from types import SimpleNamespace

import pytest

from modules.applications.application.results.pricing_result import (
    PricingResult,
)
from modules.applications.application.services.pricing_calculator import (
    PricingCalculator,
)
from modules.options.domain.enums import BillingType
from modules.vehicles.domain.enums import VehicleType


# ============================================================
# HELPERS
# ============================================================


def make_vehicle(
    *,
    price=10000,
    vehicle_type=VehicleType.SALE,
):
    return SimpleNamespace(
        price=price,
        type=vehicle_type,
    )


def make_option(
    *,
    price=100,
    billing_type=BillingType.DAILY,
):
    return SimpleNamespace(
        price=price,
        billing_type=billing_type,
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def calculator():
    return PricingCalculator()


# ============================================================
# SALE
# ============================================================


def test_sale_calculates_base_price(
    calculator,
):
    vehicle = make_vehicle(
        price=20000,
        vehicle_type=VehicleType.SALE,
    )

    result = calculator.calculate(
        vehicle=vehicle,
    )

    assert isinstance(
        result,
        PricingResult,
    )

    assert result.base_price == 20000
    assert result.optional_price == 0
    assert result.discount == 0
    assert result.total_price == 20000


def test_sale_ignores_options(
    calculator,
):
    vehicle = make_vehicle(
        price=20000,
        vehicle_type=VehicleType.SALE,
    )

    options = [
        make_option(
            price=100,
            billing_type=BillingType.DAILY,
        ),
        make_option(
            price=500,
            billing_type=BillingType.FIXED,
        ),
    ]

    result = calculator.calculate(
        vehicle=vehicle,
        options=options,
        rental_days=5,
    )

    assert result.base_price == 20000
    assert result.optional_price == 0
    assert result.total_price == 20000


# ============================================================
# RENTAL
# ============================================================


def test_rental_calculates_base_price_from_days(
    calculator,
):
    vehicle = make_vehicle(
        price=100,
        vehicle_type=VehicleType.RENT,
    )

    result = calculator.calculate(
        vehicle=vehicle,
        rental_days=5,
    )

    assert result.base_price == 500
    assert result.optional_price == 0
    assert result.discount == 0
    assert result.total_price == 500


def test_rental_with_one_day(
    calculator,
):
    vehicle = make_vehicle(
        price=150,
        vehicle_type=VehicleType.RENT,
    )

    result = calculator.calculate(
        vehicle=vehicle,
        rental_days=1,
    )

    assert result.base_price == 150
    assert result.total_price == 150


def test_rental_zero_days_uses_one_day(
    calculator,
):
    vehicle = make_vehicle(
        price=150,
        vehicle_type=VehicleType.RENT,
    )

    result = calculator.calculate(
        vehicle=vehicle,
        rental_days=0,
    )

    assert result.base_price == 150
    assert result.total_price == 150


def test_rental_negative_days_uses_one_day(
    calculator,
):
    vehicle = make_vehicle(
        price=150,
        vehicle_type=VehicleType.RENT,
    )

    result = calculator.calculate(
        vehicle=vehicle,
        rental_days=-5,
    )

    assert result.base_price == 150
    assert result.total_price == 150


# ============================================================
# RENTAL OPTIONS
# ============================================================


def test_rental_daily_option_is_multiplied_by_days(
    calculator,
):
    vehicle = make_vehicle(
        price=100,
        vehicle_type=VehicleType.RENT,
    )

    options = [
        make_option(
            price=20,
            billing_type=BillingType.DAILY,
        )
    ]

    result = calculator.calculate(
        vehicle=vehicle,
        options=options,
        rental_days=5,
    )

    assert result.base_price == 500
    assert result.optional_price == 100
    assert result.total_price == 600


def test_rental_once_option_is_not_multiplied_by_days(
    calculator,
):
    vehicle = make_vehicle(
        price=100,
        vehicle_type=VehicleType.RENT,
    )

    options = [
        make_option(
            price=300,
            billing_type=BillingType.FIXED,
        )
    ]

    result = calculator.calculate(
        vehicle=vehicle,
        options=options,
        rental_days=5,
    )

    assert result.base_price == 500
    assert result.optional_price == 300
    assert result.total_price == 800


def test_rental_combines_daily_and_once_options(
    calculator,
):
    vehicle = make_vehicle(
        price=100,
        vehicle_type=VehicleType.RENT,
    )

    options = [
        make_option(
            price=20,
            billing_type=BillingType.DAILY,
        ),
        make_option(
            price=50,
            billing_type=BillingType.DAILY,
        ),
        make_option(
            price=300,
            billing_type=BillingType.FIXED,
        ),
    ]

    result = calculator.calculate(
        vehicle=vehicle,
        options=options,
        rental_days=5,
    )

    # Base = 100 × 5 = 500
    # Daily = (20 × 5) + (50 × 5) = 350
    # Once = 300
    # Options = 650
    # Total = 1150

    assert result.base_price == 500
    assert result.optional_price == 650
    assert result.total_price == 1150


def test_rental_without_options(
    calculator,
):
    vehicle = make_vehicle(
        price=100,
        vehicle_type=VehicleType.RENT,
    )

    result = calculator.calculate(
        vehicle=vehicle,
        options=None,
        rental_days=5,
    )

    assert result.optional_price == 0
    assert result.total_price == 500


def test_rental_with_empty_options(
    calculator,
):
    vehicle = make_vehicle(
        price=100,
        vehicle_type=VehicleType.RENT,
    )

    result = calculator.calculate(
        vehicle=vehicle,
        options=[],
        rental_days=5,
    )

    assert result.optional_price == 0
    assert result.total_price == 500


# ============================================================
# DISCOUNT
# ============================================================


def test_discount_is_subtracted_from_total(
    calculator,
):
    vehicle = make_vehicle(
        price=10000,
        vehicle_type=VehicleType.SALE,
    )

    result = calculator.calculate(
        vehicle=vehicle,
        discount=1000,
    )

    assert result.base_price == 10000
    assert result.discount == 1000
    assert result.total_price == 9000


def test_negative_discount_becomes_zero(
    calculator,
):
    vehicle = make_vehicle(
        price=10000,
        vehicle_type=VehicleType.SALE,
    )

    result = calculator.calculate(
        vehicle=vehicle,
        discount=-500,
    )

    assert result.discount == 0
    assert result.total_price == 10000


def test_discount_cannot_exceed_total_before_discount(
    calculator,
):
    vehicle = make_vehicle(
        price=10000,
        vehicle_type=VehicleType.SALE,
    )

    result = calculator.calculate(
        vehicle=vehicle,
        discount=15000,
    )

    assert result.discount == 10000
    assert result.total_price == 0


def test_discount_can_equal_total(
    calculator,
):
    vehicle = make_vehicle(
        price=10000,
        vehicle_type=VehicleType.SALE,
    )

    result = calculator.calculate(
        vehicle=vehicle,
        discount=10000,
    )

    assert result.discount == 10000
    assert result.total_price == 0


def test_discount_is_capped_after_rental_options(
    calculator,
):
    vehicle = make_vehicle(
        price=100,
        vehicle_type=VehicleType.RENT,
    )

    options = [
        make_option(
            price=50,
            billing_type=BillingType.DAILY,
        )
    ]

    # Base = 100 × 2 = 200
    # Options = 50 × 2 = 100
    # Total before discount = 300

    result = calculator.calculate(
        vehicle=vehicle,
        options=options,
        rental_days=2,
        discount=500,
    )

    assert result.base_price == 200
    assert result.optional_price == 100
    assert result.discount == 300
    assert result.total_price == 0


# ============================================================
# NONE / ZERO PRICES
# ============================================================


def test_vehicle_price_none_is_treated_as_zero(
    calculator,
):
    vehicle = make_vehicle(
        price=None,
        vehicle_type=VehicleType.SALE,
    )

    result = calculator.calculate(
        vehicle=vehicle,
    )

    assert result.base_price == 0
    assert result.optional_price == 0
    assert result.total_price == 0


def test_vehicle_price_zero(
    calculator,
):
    vehicle = make_vehicle(
        price=0,
        vehicle_type=VehicleType.SALE,
    )

    result = calculator.calculate(
        vehicle=vehicle,
    )

    assert result.base_price == 0
    assert result.total_price == 0


def test_option_price_none_is_treated_as_zero(
    calculator,
):
    vehicle = make_vehicle(
        price=100,
        vehicle_type=VehicleType.RENT,
    )

    options = [
        make_option(
            price=None,
            billing_type=BillingType.DAILY,
        )
    ]

    result = calculator.calculate(
        vehicle=vehicle,
        options=options,
        rental_days=5,
    )

    assert result.base_price == 500
    assert result.optional_price == 0
    assert result.total_price == 500


def test_multiple_zero_price_options(
    calculator,
):
    vehicle = make_vehicle(
        price=100,
        vehicle_type=VehicleType.RENT,
    )

    options = [
        make_option(
            price=0,
            billing_type=BillingType.DAILY,
        ),
        make_option(
            price=0,
            billing_type=BillingType.FIXED,
        ),
    ]

    result = calculator.calculate(
        vehicle=vehicle,
        options=options,
        rental_days=5,
    )

    assert result.optional_price == 0
    assert result.total_price == 500


# ============================================================
# RENTAL DAYS NORMALIZATION
# ============================================================


@pytest.mark.parametrize(
    "rental_days",
    [
        0,
        -1,
        -10,
    ],
)
def test_rental_days_are_at_least_one_day(
    calculator,
    rental_days,
):
    vehicle = make_vehicle(
        price=100,
        vehicle_type=VehicleType.RENT,
    )

    result = calculator.calculate(
        vehicle=vehicle,
        rental_days=rental_days,
    )

    assert result.base_price == 100
    assert result.total_price == 100


# ============================================================
# RESULT CONSISTENCY
# ============================================================


def test_result_total_matches_components(
    calculator,
):
    vehicle = make_vehicle(
        price=200,
        vehicle_type=VehicleType.RENT,
    )

    options = [
        make_option(
            price=20,
            billing_type=BillingType.DAILY,
        ),
        make_option(
            price=100,
            billing_type=BillingType.FIXED,
        ),
    ]

    result = calculator.calculate(
        vehicle=vehicle,
        options=options,
        rental_days=3,
        discount=50,
    )

    assert result.total_price == (
        result.base_price
        + result.optional_price
        - result.discount
    )