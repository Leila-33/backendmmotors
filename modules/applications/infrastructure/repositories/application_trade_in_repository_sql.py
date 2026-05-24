from sqlalchemy.orm import Session
from modules.applications.domain.repositories.application_trade_in_repository import ApplicationTradeInRepository
from modules.applications.infrastructure.db.application_trade_in_model import ApplicationTradeInModel

class ApplicationTradeInRepositorySQL(ApplicationTradeInRepository):

    def __init__(self, db: Session):
        self.db = db

    def delete_by_application(self, application_id: str):

        self.db.query(ApplicationTradeInModel)\
            .filter(ApplicationTradeInModel.application_id == application_id)\
            .delete()

        self.db.commit()