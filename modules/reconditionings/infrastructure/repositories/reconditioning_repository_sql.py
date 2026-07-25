from typing import Optional
from sqlalchemy.orm import Session
from modules.reconditionings.domain.entities.reconditioning import Reconditioning
from modules.reconditionings.infrastructure.db.reconditioning_model import ReconditioningModel
from modules.reconditionings.domain.repositories.reconditioning_repository import ReconditioningRepository
from modules.reconditionings.infrastructure.mapper.reconditioning_mapper import ReconditioningMapper

class ReconditioningRepositorySQL(
    ReconditioningRepository
):

    def __init__(
        self,
        db: Session
    ):
        self.db = db



    # =========================
    # GET BY ID
    # =========================

    def get_by_id(
        self,
        reconditioning_id: str
    ) -> Optional[Reconditioning]:


        model = (
            self.db.query(
                ReconditioningModel
            )
            .filter(
                ReconditioningModel.id
                == reconditioning_id
            )
            .first()
        )


        if not model:
            return None


        return ReconditioningMapper.to_domain(
            model
        )



    # =========================
    # GET BY VEHICLE ID
    # =========================

    def get_by_vehicle_id(
        self,
        vehicle_id: str
    ) -> Optional[Reconditioning]:


        model = (
            self.db.query(
                ReconditioningModel
            )
            .filter(
                ReconditioningModel.vehicle_id
                == vehicle_id
            )
            .first()
        )


        if not model:
            return None


        return ReconditioningMapper.to_domain(
            model
        )



    # =========================
    # SAVE
    # =========================

    def save(
        self,
        reconditioning: Reconditioning
    ) -> None:


        model = (
            ReconditioningMapper.to_model(
                reconditioning
            )
        )


        self.db.add(model)

        self.db.flush()



    # =========================
    # UPDATE
    # =========================

    def update(
        self,
        reconditioning: Reconditioning
    ) -> None:


        model = (
            self.db.query(
                ReconditioningModel
            )
            .filter(
                ReconditioningModel.id
                == reconditioning.id
            )
            .first()
        )


        if not model:
            return None



        ReconditioningMapper.update_model(
            model,
            reconditioning
        )


        self.db.flush()

