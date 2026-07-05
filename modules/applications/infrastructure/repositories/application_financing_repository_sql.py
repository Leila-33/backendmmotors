from sqlalchemy.orm import Session
from modules.applications.domain.repositories.application_financing_repository import ApplicationFinancingRepository
from modules.applications.infrastructure.db.application_financing_model import ApplicationFinancingModel
class ApplicationFinancingRepositorySQL(ApplicationFinancingRepository):

    def __init__(self, db: Session):
        self.db = db

    def delete_by_application(self, application_id: str):

        self.db.query(ApplicationFinancingModel)\
            .filter(ApplicationFinancingModel.application_id == application_id)\
            .delete()

        self.db.commit()