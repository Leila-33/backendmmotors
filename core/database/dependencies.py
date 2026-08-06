from fastapi import Depends
from sqlalchemy.orm import Session
from .session import SessionLocal
from .unit_of_work import UnitOfWork


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()



def get_unit_of_work(
    db: Session = Depends(get_db),
):
    return UnitOfWork(db)