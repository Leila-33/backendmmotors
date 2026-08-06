from core.database.session import SessionLocal
from core.database.unit_of_work import UnitOfWork

from modules.reservations.infrastructure.repositories.reservation_repository_sql import ReservationRepositorySQL
from modules.applications.infrastructure.repositories.event_repository_sql import EventRepositorySQL
from modules.applications.infrastructure.repositories.application_repository_sql import ApplicationRepositorySQL

from modules.reservations.application.use_cases.complete_expired_rentals import (
    CompleteExpiredRentalsUseCase,
)


def create_complete_rentals_usecase():

    db = SessionLocal()

    return (
        CompleteExpiredRentalsUseCase(
            reservation_repository=ReservationRepositorySQL(db),
            event_repository=EventRepositorySQL(db),
            application_repository=ApplicationRepositorySQL(db),
            unit_of_work=UnitOfWork(db),
        ),
        db,
    )

def run_complete_rentals():

    usecase, db = create_complete_rentals_usecase()

    try:
        usecase.execute()
    finally:
        db.close()