from modules.reservations.infrastructure.repositories.reservation_repository_sql import ReservationRepositorySQL
from infrastructure.db.dependencies import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

from modules.reservations.application.use_cases.reservation import (
    CreateReservationUseCase,
    CancelReservationUseCase
)

def get_repo(db: Session = Depends(get_db)):
    return ReservationRepositorySQL(db)
    

def get_create_uc(repo=Depends(get_repo)):
    return CreateReservationUseCase(repo)


def get_cancel_uc(repo=Depends(get_repo)):
    return CancelReservationUseCase(repo)