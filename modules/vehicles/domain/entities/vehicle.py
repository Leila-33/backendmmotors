from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from modules.warranties.domain.entities.vehicle_warranty import (
    VehicleWarranty,
)

from modules.vehicles.domain.enums import (
    VehicleCondition,
    VehicleType,
    EngineType,
    VehicleStatus,
)

from modules.vehicles.domain.exceptions import (
    VehicleCannotBeMarkedAsInspected,
    VehicleNotEligibleForInspection,
    VehicleCannotStartReconditioning,
    VehicleCannotBeMarkedAsReconditioned,
    VehicleCannotBeMarkedAsReady,
    VehicleCannotBePublished,
)

from modules.inspections.domain.exceptions import (
    InspectionAlreadyCompleted,
    InspectionAlreadyRunning,
)

from modules.vehicles.domain.entities.vehicle_option import (
    VehicleOption,
)


@dataclass
class Vehicle:

    id: str

    brand: str
    model: str
    price: float

    type: VehicleType

    mileage: int
    year: int

    description: Optional[str] = None

    engine_type: Optional[EngineType] = None

    equipments: List[str] = field(
        default_factory=list
    )

    condition: VehicleCondition = (
        VehicleCondition.USED
    )

    is_available: bool = False

    published_at: Optional[datetime] = None

    images: List[str] = field(
        default_factory=list
    )

    license_plate: Optional[str] = None

    warranty: Optional[VehicleWarranty] = None

    options: List[VehicleOption] = field(
        default_factory=list
    )

    status: VehicleStatus = (
        VehicleStatus.AVAILABLE
    )

    final_check_at: Optional[datetime] = None

    # =====================================================
    # INSPECTION
    # =====================================================

    def ensure_can_be_inspected(self):

        if self.status == VehicleStatus.INSPECTION_PENDING:
            raise InspectionAlreadyRunning()

        if self.status == VehicleStatus.INSPECTED:
            raise InspectionAlreadyCompleted()

        if self.status != VehicleStatus.AVAILABLE:
            raise VehicleNotEligibleForInspection()

    def request_inspection(self):

        self.status = VehicleStatus.INSPECTION_PENDING

    def mark_as_inspected(self):

        if self.status == VehicleStatus.INSPECTED:
            raise VehicleCannotBeMarkedAsInspected()

        self.status = VehicleStatus.INSPECTED

    # =====================================================
    # RECONDITIONING
    # =====================================================

    def start_reconditioning(self):

        if self.status != VehicleStatus.INSPECTED:
            raise VehicleCannotStartReconditioning()

        self.status = VehicleStatus.RECONDITIONING

    def mark_as_reconditioned(self):

        if self.status != VehicleStatus.RECONDITIONING:
            raise VehicleCannotBeMarkedAsReconditioned()

        self.status = VehicleStatus.RECONDITIONED

    # =====================================================
    # FINAL CHECK
    # =====================================================

    def mark_as_ready(self):

        if self.status != VehicleStatus.RECONDITIONED:
            raise VehicleCannotBeMarkedAsReady()

        self.status = VehicleStatus.READY

    # =====================================================
    # PUBLICATION
    # =====================================================

    def publish(self):

        if self.status != VehicleStatus.READY:
            raise VehicleCannotBePublished()

        self.status = VehicleStatus.PUBLISHED

        self.is_available = True

        self.published_at = datetime.now(
            timezone.utc
        )

    def archive(self):
        self.status = VehicleStatus.ARCHIVED
        self.is_available = False
        self.published_at = None