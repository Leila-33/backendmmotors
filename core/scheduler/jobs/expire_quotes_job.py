from core.database.session import SessionLocal
from core.database.unit_of_work import UnitOfWork
from modules.quotes.infrastructure.repositories.quote_repository_sql import (
    QuoteRepositorySQL,
)
from modules.quotes.application.use_cases.expire_quotes import ExpireQuotesUseCase
from modules.applications.application.services.event_service import EventService
from modules.applications.infrastructure.repositories.event_repository_sql import EventRepositorySQL

def create_expire_quotes_usecase():

    db = SessionLocal()

    return (
        ExpireQuotesUseCase(
            quote_repository=QuoteRepositorySQL(db),
            event_service=EventService(
                EventRepositorySQL(db)
            ),
            unit_of_work=UnitOfWork(db),
        ),
        db,
    )

def run_expire_quotes():

    usecase, db = create_expire_quotes_usecase()

    try:

        usecase.execute()

    finally:

        db.close()