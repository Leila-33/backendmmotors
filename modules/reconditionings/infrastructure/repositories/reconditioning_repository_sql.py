from typing import Optional, List

from sqlalchemy.orm import Session

from modules.reconditionings.domain.entities.reconditioning import Reconditioning
from modules.core.enums import ReconditioningStatus
from modules.reconditionings.infrastructure.db.reconditioning_model import ReconditioningModel


class ReconditioningRepositorySQL:

    def __init__(self, session: Session):
        self.session = session

    # =========================
    # GET BY ID
    # =========================
    def get_by_id(self, reconditioning_id: str) -> Optional[Reconditioning]:
        row = (
            self.session.query(ReconditioningModel)
            .filter(ReconditioningModel.id == reconditioning_id)
            .first()
        )

        return self._to_domain(row) if row else None

    # =========================
    # GET BY VEHICLE
    # =========================
    def get_by_vehicle_id(self, vehicle_id: str) -> Optional[Reconditioning]:
        row = (
            self.session.query(ReconditioningModel)
            .filter(ReconditioningModel.vehicle_id == vehicle_id)
            .first()
        )

        return self._to_domain(row) if row else None

    # =========================
    # SAVE
    # =========================
    def save(self, reconditioning: Reconditioning) -> None:
        model = self._to_model(reconditioning)
        self.session.add(model)
        self.session.commit()

    # =========================
    # UPDATE
    # =========================
    def update(self, reconditioning: Reconditioning) -> None:
        model = (
            self.session.query(ReconditioningModel)
            .filter(ReconditioningModel.id == reconditioning.id)
            .first()
        )

        if not model:
            return

        model.status = reconditioning.status
        model.cost = reconditioning.cost
        model.duration_days = reconditioning.duration_days
        model.tasks = reconditioning.tasks
        model.started_at = reconditioning.started_at
        model.completed_at = reconditioning.completed_at

        self.session.commit()

    # =========================
    # LIST BY STATUS
    # =========================
    def list_by_status(self, status: ReconditioningStatus) -> List[Reconditioning]:
        rows = (
            self.session.query(ReconditioningModel)
            .filter(ReconditioningModel.status == status)
            .all()
        )

        return [self._to_domain(r) for r in rows]

    # =========================
    # MAPPERS
    # =========================
    def _to_domain(self, row: ReconditioningModel) -> Reconditioning:
        return Reconditioning(
            id=row.id,
            vehicle_id=row.vehicle_id,
            status=row.status,
            cost=row.cost,
            duration_days=row.duration_days,
            tasks=row.tasks or [],
            started_at=row.started_at,
            completed_at=row.completed_at,
        )

    def _to_model(self, entity: Reconditioning) -> ReconditioningModel:
        return ReconditioningModel(
            id=entity.id,
            vehicle_id=entity.vehicle_id,
            status=entity.status,
            cost=entity.cost,
            duration_days=entity.duration_days,
            tasks=entity.tasks,
            started_at=entity.started_at,
            completed_at=entity.completed_at,
        )