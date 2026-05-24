from sqlalchemy.orm import Session
from modules.applications.domain.repositories.application_option_repository import ApplicationOptionRepository
from modules.applications.infrastructure.db.application_option_model import ApplicationOptionModel

class ApplicationOptionRepositorySQL(ApplicationOptionRepository):

    def __init__(self, db: Session):
        self.db = db

    def delete_by_application(self, application_id: str):

        self.db.query(ApplicationOptionModel)\
            .filter(ApplicationOptionModel.application_id == application_id)\
            .delete()

        self.db.commit()
        self.db.commit()