from modules.reconditionings.api.schemas import ReconditioningResult
from modules.inspections.domain.entities.inspection import Inspection
from modules.reconditionings.api.schemas import ReconditioningResult
from modules.core.exceptions import InvalidRepairConfiguration

def perform_reconditioning_analysis(
    inspection: Inspection,
) -> ReconditioningResult:


    # =========================
    # MAPPING CODES → BUSINESS LOGIC
    # =========================
    REPAIR_RULES = {
        "ENGINE_DIAG": {
            "cost": 800,
            "duration_days": 2,
        },
        "BRAKES_REPLACE": {
            "cost": 300,
            "duration_days": 1,
        },
        "TIRES_REPLACE": {
            "cost": 500,
            "duration_days": 1,
        },
        "ELECTRONICS_DIAG": {
            "cost": 250,
            "duration_days": 1,
        },
        "SAFETY_COMPLIANCE": {
            "cost": 600,
            "duration_days": 2,
        },
    }

    tasks = inspection.recommended_repairs or []

    cost = 0
    duration_days = 0

    for task in tasks:

        rule = REPAIR_RULES.get(task)

        if not rule:
            raise InvalidRepairConfiguration(task)

        cost += rule["cost"]
        duration_days += rule["duration_days"]

    if not tasks:
        tasks = ["NO_REPAIR_NEEDED"]
        duration_days = 1


    return ReconditioningResult(
        tasks=tasks,
        cost=cost,
        duration_days=duration_days,
    )