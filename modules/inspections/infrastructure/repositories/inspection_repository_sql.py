from sqlalchemy.orm import Session
from typing import Optional
from modules.inspections.infrastructure.db.inspection_model import InspectionModel
from modules.inspections.infrastructure.mapper.inspection_mapper import InspectionMapper
from modules.inspections.domain.entities.inspection import Inspection
from modules.inspections.domain.repositories.inspection_repository import InspectionRepository


class InspectionRepositorySQL(InspectionRepository):


    def __init__(
        self,
        db: Session
    ):
        self.db = db



    # =========================
    # SAVE
    # =========================

    def save(
        self,
        inspection: Inspection
    ) -> None:


        model = InspectionMapper.to_model(
            inspection
        )


        self.db.add(
            model
        )

        self.db.flush()



    # =========================
    # UPDATE
    # =========================

    def update(
        self,
        inspection: Inspection
    ) -> None:


        model = (
            self.db.query(
                InspectionModel
            )
            .filter(
                InspectionModel.id == inspection.id
            )
            .first()
        )


        if not model:
            return


        InspectionMapper.update_model(
            model,
            inspection
        )


        self.db.flush()



    # =========================
    # GET BY ID
    # =========================

    def get_by_id(
        self,
        inspection_id: str
    ) -> Optional[Inspection]:


        model = (
            self.db.query(
                InspectionModel
            )
            .filter(
                InspectionModel.id == inspection_id
            )
            .first()
        )


        if not model:
            return None


        return InspectionMapper.to_domain(
            model
        )



    # =========================
    # GET BY VEHICLE
    # =========================

    def get_by_vehicle_id(
        self,
        vehicle_id: str
    ) -> Optional[Inspection]:


        model = (
            self.db.query(
                InspectionModel
            )
            .filter(
                InspectionModel.vehicle_id == vehicle_id
            )
            .first()
        )


        if not model:
            return None


        return InspectionMapper.to_domain(
            model
        )