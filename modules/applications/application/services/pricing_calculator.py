from modules.vehicles.domain.enums import VehicleType
from modules.applications.application.results.pricing_result import PricingResult
from modules.options.domain.enums import BillingType

class PricingCalculator:
    """
    Calcule le prix d'une application M-Motors.
    """
    def calculate(
        self,
        vehicle,
        options: list | None = None,
        discount: float = 0,
        rental_days: int = 1,
    ) -> PricingResult:

        # =========================
        # PRIX DE BASE
        # =========================

        vehicle_price = float(
            vehicle.price or 0
        )

        # =========================
        # LOCATION
        # =========================

        if vehicle.type == VehicleType.RENT:

            rental_days = max(
                rental_days,
                1,
            )

            base_price = (
                vehicle_price
                * rental_days
            )

            optional_price = (
                self._calculate_rental_options(
                    options or [],
                    rental_days,
                )
            )

        # =========================
        # VENTE
        # =========================

        else:

            base_price = vehicle_price
            optional_price = 0

        # =========================
        # REMISE
        # =========================

        discount = max(
            float(discount or 0),
            0,
        )

        discount = min(
            discount,
            base_price + optional_price,
        )

        # =========================
        # TOTAL
        # =========================

        total_price = (
            base_price
            + optional_price
            - discount
        )

        return PricingResult(
            base_price=base_price,
            optional_price=optional_price,
            discount=discount,
            total_price=total_price,
        )

    def _calculate_rental_options(
        self,
        options: list,
        rental_days: int,
    ) -> float:

        total = 0

        for option in options:

            option_price = float(
                option.price or 0
            )

            if option.billing_type == BillingType.DAILY:

                total += (
                    option_price
                    * rental_days
                )

            else:

                total += option_price

        return total