from datetime import datetime

from modules.financing.domain.entities.trade_in_input import TradeInInput


class TradeInService:

    @staticmethod
    def estimate(data: TradeInInput) -> int:

        current_year = datetime.now().year

        # =========================
        # AGE
        # =========================
        age = max(0, current_year - data.year)

        depreciation = 0.14

        age_factor = (1 - depreciation) ** age

        # =========================
        # MILEAGE
        # =========================
        expected_mileage = max(15000, age * 15000)

        mileage_ratio = data.mileage / expected_mileage

        if mileage_ratio <= 1:
            mileage_factor = 1 - (mileage_ratio * 0.1)
        else:
            mileage_factor = 1 - ((mileage_ratio - 1) * 0.25)

        mileage_factor = max(0.4, mileage_factor)

        # =========================
        # CONDITION
        # =========================
        condition_map = {
            "excellent": 1.1,
            "good": 1.0,
            "average": 0.85,
            "poor": 0.7
        }

        condition_factor = condition_map.get(
            data.condition,
            1.0
        )

        # =========================
        # BASE VALUE
        # =========================
        base = 20000

        value = (
            base
            * age_factor
            * mileage_factor
            * condition_factor
        )

        return int(round(max(1000, value)))