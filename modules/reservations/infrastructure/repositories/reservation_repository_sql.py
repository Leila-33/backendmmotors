from sqlalchemy.orm import Session

from modules.reservations.infrastructure.db.reservation_model import ReservationModel
from modules.reservations.domain.entities.reservation import Reservation
from modules.core.enums import ReservationStatus


class ReservationRepositorySQL:

    def __init__(self, db: Session):
        self.db = db

    # 🔄 mapping DB → DOMAIN
    def _to_domain(self, obj: ReservationModel) -> Reservation:
        return Reservation(
            id=obj.id,
            vehicle_id=obj.vehicle_id,
            user_id=obj.user_id,
            start_date=obj.start_date,
            end_date=obj.end_date,
            status=obj.status,
            created_at=obj.created_at,
            updated_at=obj.updated_at
        )

    # 🔄 DOMAIN → DB
    def _to_db(self, domain: Reservation) -> ReservationModel:
        return ReservationModel(
            vehicle_id=domain.vehicle_id,
            user_id=domain.user_id,
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
    

 