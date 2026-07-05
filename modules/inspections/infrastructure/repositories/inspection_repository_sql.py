from sqlalchemy.orm import Session

from modules.inspections.infrastructure.db.inspection_model import InspectionModel
from modules.inspections.infrastructure.mapper.inspection_mapper import InspectionMapper
from modules.inspections.domain.entities.inspection import Inspection


class InspectionRepositorySQL:

    def __init__(self, session: Session):
        self.session = session

    # =========================
    # SAVE
    # =========================
    def save(self, inspection: Inspection) -> None:
        model = InspectionMapper.to_model(inspection)
        self.session.add(model)

    # =========================
    # UPDATE
    # =========================
    def update(self, inspection: Inspection) -> None:
        model = (
            self.session.query(InspectionModel)
            .filter_by(id=inspection.id)
            .first()
        )

        if not model:
            return

        updated = InspectionMapper.to_model(inspection)

        for key, value in updated.__dict__.items():
            if key != "_sa_instance_state":
                setattr(model, key, value)

    # =========================
    # GET BY ID
    # =========================
    def get_by_id(self, inspection_id: str) -> Inspection | None:
        model = (
            self.session.query(InspectionModel)
            .filter_by(id=inspection_id)
            .first()
        )

        return InspectionMapper.to_domain(model) if model else None

    # =========================
    # GET BY VEHICLE
    # =========================
    def get_by_vehicle_id(self, vehicle_id: str) -> Inspection | None:
        model = (
            self.session.query(InspectionModel)
            .filter_by(vehicle_id=vehicle_id)
            .order_by(InspectionModel.created_at.desc())
            .first()
        )

        return InspectionMapper.to_domain(model) if model else None