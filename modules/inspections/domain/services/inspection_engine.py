from modules.inspections.domain.entities.inspection_result import (
    InspectionResult,
)


class InspectionEngine:

    def run(self, vehicle) -> InspectionResult:

        failures = []
        repairs = []

        # =====================================================
        # MOTEUR
        # =====================================================

        engine_score = self._score_engine(vehicle)

        if engine_score < 60:
            failures.append("ENGINE_LOW")
            repairs.append("ENGINE_DIAG")

        # =====================================================
        # FREINS
        # =====================================================

        brakes_score = self._score_brakes(vehicle)

        if brakes_score < 50:
            failures.append("BRAKES_WORN")
            repairs.append("BRAKES_REPLACE")

        # =====================================================
        # PNEUS
        # =====================================================

        tires_score = self._score_tires(vehicle)

        if tires_score < 50:
            failures.append("TIRES_WORN")
            repairs.append("TIRES_REPLACE")

        # =====================================================
        # ÉLECTRONIQUE
        # =====================================================

        electronics_score = self._score_electronics(vehicle)

        if electronics_score < 60:
            failures.append("ELECTRONICS_FAULT")
            repairs.append("ELECTRONICS_DIAG")

        # =====================================================
        # SAFETY SCORE
        # =====================================================

        safety_score = int(
            (
                brakes_score
                + tires_score
            ) / 2
        )

        # =====================================================
        # OVERALL SCORE
        # =====================================================

        overall_score = int(
            (
                engine_score
                + brakes_score
                + tires_score
                + electronics_score
            ) / 4
        )

        # =====================================================
        # RESULT
        # =====================================================

        return InspectionResult(
            engine_score=engine_score,
            brakes_score=brakes_score,
            tires_score=tires_score,
            electronics_score=electronics_score,
            safety_score=safety_score,
            overall_score=overall_score,
            failures=failures,
            recommended_repairs=repairs,
        )

    # =========================
    # INTERNAL RULES
    # =========================

    def _score_engine(self, vehicle) -> int:
        base = 80

        if vehicle.mileage > 150000:
            base -= 20
        if vehicle.year < 2012:
            base -= 15

        return max(0, min(100, base))

    def _score_brakes(self, vehicle) -> int:
        base = 85

        if vehicle.mileage > 100000:
            base -= 25

        return max(0, min(100, base))

    def _score_tires(self, vehicle) -> int:
        base = 80

        if vehicle.mileage > 120000:
            base -= 30

        return max(0, min(100, base))

    def _score_electronics(self, vehicle) -> int:
        base = 90

        if vehicle.year < 2015:
            base -= 20

        return max(0, min(100, base))