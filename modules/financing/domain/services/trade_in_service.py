from datetime import datetime

from modules.financing.domain.inputs.trade_in_input import TradeInInput
from modules.applications.domain.enums import TradeInVehicleCondition
from modules.financing.application.results.trade_in_estimate_result import TradeInEstimateResult

class TradeInService:

    @staticmethod
    def estimate(
        data: TradeInInput,
    ) -> TradeInEstimateResult:

        current_year = datetime.now().year

        age = max(
            0,
            current_year - data.year,
        )

        depreciation = 0.14

        age_factor = (
            1 - depreciation
        ) ** age

        expected_mileage = max(
            15_000,
            age * 15_000,
        )

        mileage_ratio = (
            data.mileage / expected_mileage
        )

        if mileage_ratio <= 1:
            mileage_factor = (
                1 - mileage_ratio * 0.1
            )
        else:
            mileage_factor = (
                1 - (mileage_ratio - 1) * 0.25
            )

        mileage_factor = max(
            0.4,
            mileage_factor,
        )

        condition_map = {
            TradeInVehicleCondition.EXCELLENT: 1.1,
            TradeInVehicleCondition.GOOD: 1.0,
            TradeInVehicleCondition.AVERAGE: 0.85,
            TradeInVehicleCondition.POOR: 0.7,
        }

        condition_factor = condition_map.get(
            data.condition,
            1.0,
        )

        base_value = 20_000

        estimated_value = int(
            round(
                max(
                    1_000,
                    base_value
                    * age_factor
                    * mileage_factor
                    * condition_factor,
                )
            )
        )

        return TradeInEstimateResult(
            estimated_value=estimated_value,
        )