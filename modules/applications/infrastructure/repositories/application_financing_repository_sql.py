from sqlalchemy.orm import Session

from modules.applications.domain.repositories.application_financing_repository import (
    ApplicationFinancingRepository
)

from modules.applications.domain.entities.application_financing import (
    ApplicationFinancing
)
from modules.applications.infrastructure.db.application_financing_model import (
    ApplicationFinancingModel
)

from modules.applications.infrastructure.mappers.application_financing_mapper import (
    ApplicationFinancingMapper
)


class ApplicationFinancingRepositorySQL(
    ApplicationFinancingRepository
):

    def __init__(
        self,
        db: Session
    ):
        self.db = db


    # =========================
    # SAVE / UPDATE FINANCING
    # =========================
    def save(
        self,
        financing: ApplicationFinancing
    ):

        existing = (
            self.db.query(ApplicationFinancingModel)
            .filter_by(
                application_id=financing.application_id
            )
            .first()
        )


        if existing:

            # Mise à jour du modèle SQLAlchemy existant
            ApplicationFinancingMapper.update_model(
                existing,
                financing
            )


        else:

            # Création d'un nouveau modèle
            existing = ApplicationFinancingMapper.to_model(
                financing
            )

            self.db.add(existing)


        self.db.flush()


        return ApplicationFinancingMapper.to_domain(
            existing
        )



    # =========================
    # GET BY APPLICATION
    # =========================
    def get_by_application(
        self,
        application_id: str
    ):

        model = (
            self.db.query(
                ApplicationFinancingModel
            )
            .filter_by(
                application_id=application_id
            )
            .first()
        )


        if not model:
            return None


        return ApplicationFinancingMapper.to_domain(
            model
        )



    # =========================
    # DELETE BY APPLICATION
    # =========================
    def delete_by_application(
        self,
        application_id: str
    ) -> None:

        (
            self.db.query(
                ApplicationFinancingModel
            )
            .filter(
                ApplicationFinancingModel.application_id == application_id
            )
            .delete(
                synchronize_session=False
            )
        )

        self.db.flush()
