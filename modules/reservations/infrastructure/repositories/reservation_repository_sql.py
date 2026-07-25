from sqlalchemy.orm import Session

from modules.reservations.infrastructure.db.reservation_model import ReservationModel
from modules.reservations.domain.entities.reservation import Reservation
from modules.applications.domain.enums import ApplicationStatus
from modules.reservations.domain.enums import ReservationStatus
from modules.applications.infrastructure.db.application_model import ApplicationModel
from uuid import uuid4
from datetime import date

class ReservationRepositorySQL:

    def __init__(self, db: Session):
        self.db = db

    # 🔄 mapping DB → DOMAIN
    def _to_domain(self, obj: ReservationModel) -> Reservation:
        return Reservation(
            id=obj.id,
            vehicle_id=obj.vehicle_id,
            application_id=obj.application_id,
            start_date=obj.start_date,
            end_date=obj.end_date,
            status=obj.status,
            created_at=obj.created_at,
            updated_at=obj.updated_at
        )

    # 🔄 DOMAIN → DB
    def _to_db(self, domain: Reservation) -> ReservationModel:
        return ReservationModel(
            id=domain.id,
            vehicle_id=domain.vehicle_id,
            application_id=domain.application_id,
            start_date=domain.start_date,
            end_date=domain.end_date,
            status=domain.status
        )

    def create(self, domain: Reservation):
        obj = self._to_db(domain)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return self._to_domain(obj)

    def get_by_id(self, reservation_id: int):
        obj = self.db.query(ReservationModel).filter_by(id=reservation_id).first()
        return self._to_domain(obj) if obj else None

    def cancel(self, reservation_id: int):
        obj = self.db.query(ReservationModel).filter_by(id=reservation_id).first()
        if not obj:
            return None

        obj.status = ReservationStatus.CANCELLED
        self.db.commit()

        return self._to_domain(obj)

    def exists_overlap(self, vehicle_id, start_date, end_date):
        return self.db.query(ReservationModel).filter(
            ReservationModel.vehicle_id == vehicle_id,
            ReservationModel.status == ReservationStatus.ACTIVE,
            ReservationModel.start_date <= end_date,
            ReservationModel.end_date >= start_date
        ).first() is not None
    

    def find_finished_rentals(self, now):
        return (
            self.db.query(ReservationModel)
            .join(ApplicationModel)
            .filter(
                ReservationModel.end_date < now,
                ApplicationModel.status == ApplicationStatus.PAID,
                ApplicationModel.deleted_at.is_(None)
            )
            .all()
        )
    def get_by_application_id(self, application_id: str):

        return (
            self.db
            .query(ReservationModel)
            .filter(
                ReservationModel.application_id == application_id
            )
            .first()
        )
            
    def create_or_update(
    self,
    application_id: str,
    vehicle_id: str,
    start_date: date,
    end_date: date,
    status: ReservationStatus
):

        orm_reservation = self.get_by_application_id(application_id)

        # =========================
        # UPDATE
        # =========================
        if orm_reservation:

            orm_reservation.start_date = start_date
            orm_reservation.end_date = end_date
            orm_reservation.status = status

            self.db.commit()
            self.db.refresh(orm_reservation)

            return orm_reservation

        # =========================
        # CREATE (DOMAIN → ORM)
        # =========================

        domain = Reservation(
            id=str(uuid4()),
            application_id=application_id,
            vehicle_id=vehicle_id,
            start_date=start_date,
            end_date=end_date,
            status=status
        )

        orm_reservation = self._to_db(domain)

        self.db.add(orm_reservation)
        self.db.commit()
        self.db.refresh(orm_reservation)

        return orm_reservation
    
    def delete_by_application_id(
    self,
    application_id: str
):
        reservation = (
            self.db.query(ReservationModel)
            .filter(
                ReservationModel.application_id == application_id
            )
            .first()
        )

        if reservation:
            self.db.delete(reservation)
    
    def get_active_by_vehicle_id(
    self,
    vehicle_id: str
):

        return (
            self.db
            .query(ReservationModel)
            .filter(
                ReservationModel.vehicle_id == vehicle_id,
                ReservationModel.status.in_([
                    ReservationStatus.ACTIVE,
                    ReservationStatus.DRAFT
                ])
            )
            .all()
        )