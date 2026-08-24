from dataclasses import dataclass

from modules.inspections.domain.entities.inspection import Inspection
from modules.reconditionings.domain.entities.reconditioning import Reconditioning


@dataclass(frozen=True)
class GetVehicleLifecycleResult:
    inspection: Inspection | None
    reconditioning: Reconditioning | None