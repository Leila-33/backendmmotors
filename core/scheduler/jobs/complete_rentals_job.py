from core.database.session import SessionLocal
from core.database.unit_of_work import UnitOfWork

from modules.reservations.infrastructure.repositories.reservation_repository_sql import ReservationRepositorySQL
from modules.applications.infrastructure.repositories.event_repository_sql import EventRepositorySQL
from modules.applications.infrastructure.repositories.application_repository_sql import ApplicationRepositorySQL
from modules.applications.application.services.event_service import EventService
from modules.reservations.application.use_cases.complete_expired_rentals import (
    CompleteExpiredRentalsUseCase,
)



def create_complete_rentals_usecase():
    db = SessionLocal()

    event_repository = EventRepositorySQL(db)
    event_service = EventService(event_repository)

    usecase = CompleteExpiredRentalsUseCase(
        reservation_repository=ReservationRepositorySQL(db),
        application_repository=ApplicationRepositorySQL(db),
        event_service=event_service,
        unit_of_work=UnitOfWork(db),
    )

    return usecase, db    

def run_complete_rentals():

    usecase, db = create_complete_rentals_usecase()

    try:
        usecase.execute()
    finally:
        db.close()