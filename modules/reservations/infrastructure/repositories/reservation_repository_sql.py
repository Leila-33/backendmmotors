from sqlalchemy.orm import Session
from modules.reservations.infrastructure.db.reservation_model import ReservationModel
from modules.reservations.domain.entities.reservation import Reservation
from modules.applications.domain.enums import ApplicationStatus
from modules.reservations.domain.enums import ReservationStatus
from modules.applications.infrastructure.db.application_model import ApplicationModel
from uuid import uuid4
from datetime import date
from modules.reservations.domain.entities.reservation import Reservation
from modules.reservations.infrastructure.db.reservation_model import ReservationModel
from modules.reservations.infrastructure.mapper.reservation_mapper import ReservationMapper
from datetime import datetime
from modules.reservations.domain.exceptions import ReservationNotFound

class ReservationRepositorySQL:


    def __init__(self, db: Session):
        self.db = db

    # =========================
    # GET BY ID
    # =========================
    def get_by_id(
        self,
        reservation_id: str
    ) -> Reservation | None:

        model = (
            self.db.query(ReservationModel)
            .filter_by(id=reservation_id)
            .first()
        )

        if not model:
            return None

        return ReservationMapper.to_domain(model)



    # =========================
    # CANCEL
    # =========================
    def cancel(
        self,
        reservation_id: str
    ) -> Reservation | None:


        model = (
            self.db.query(ReservationModel)
            .filter_by(id=reservation_id)
            .first()
        )


        if not model:
            return None


        model.status = ReservationStatus.CANCELLED

        self.db.flush()


        return ReservationMapper.to_domain(
            model
        )



    # =========================
    # OVERLAP CHECK
    # =========================
    def exists_overlap(
        self,
        vehicle_id: str,
        start_date: date,
        end_date: date,
        exclude_application_id: str | None = None,
    ) -> bool:

        query = (
            self.db.query(ReservationModel)
            .filter(
                ReservationModel.vehicle_id == vehicle_id,

                ReservationModel.status == ReservationStatus.ACTIVE,

                ReservationModel.start_date <= end_date,

                ReservationModel.end_date >= start_date,
            )
        )


        # =========================
        # EXCLUDE CURRENT APPLICATION
        # =========================
        if exclude_application_id:

            query = query.filter(
                ReservationModel.application_id
                != exclude_application_id
            )


        return query.first() is not None



    # =========================
    # FINISHED RENTALS
    # =========================
    def find_expired_active(
        self,
        now: datetime,
    ) -> list[Reservation]:

        models = (
            self.db.query(ReservationModel)
            .join(ApplicationModel)
            .filter(
                ReservationModel.status == ReservationStatus.ACTIVE,
                ReservationModel.end_date < now.date(),
                ApplicationModel.status == ApplicationStatus.PAID,
                ApplicationModel.deleted_at.is_(None),
            )
            .all()
        )

        return [
            ReservationMapper.to_domain(model)
            for model in models
        ]



    # =========================
    # BY APPLICATION
    # =========================
    def get_by_application_id(
        self,
        application_id: str
    ) -> Reservation | None:


        model = (
            self.db.query(ReservationModel)
            .filter(
                ReservationModel.application_id == application_id
            )
            .first()
        )


        if not model:
            return None


        return ReservationMapper.to_domain(
            model
        )



    # =========================
    # CREATE OR UPDATE
    # =========================
    def create_or_update(
        self,
        application_id: str,
        vehicle_id: str,
        start_date: date,
        end_date: date,
        status: ReservationStatus
    ) -> Reservation:


        model = (
            self.db.query(ReservationModel)
            .filter(
                ReservationModel.application_id == application_id
            )
             .first()
        )


        # UPDATE
        if model:

            model.start_date = start_date
            model.end_date = end_date
            model.status = status

            self.db.flush()

            return ReservationMapper.to_domain(
                model
            )


        # CREATE

        domain = Reservation(
            id=str(uuid4()),
            application_id=application_id,
            vehicle_id=vehicle_id,
            start_date=start_date,
            end_date=end_date,
            status=status
        )


        model = ReservationMapper.to_model(
            domain
        )


        self.db.add(model)
        self.db.flush()


        return ReservationMapper.to_domain(
            model
        )



    # =========================
    # DELETE BY APPLICATION
    # =========================
    def delete_by_application(
        self,
        application_id: str
    ) -> None:


        (
            self.db.query(ReservationModel)
            .filter(
                ReservationModel.application_id == application_id
            )
            .delete(
                synchronize_session=False
            )
        )

        self.db.flush()



    # =========================
    # ACTIVE BY VEHICLE
    # =========================
    def get_active_by_vehicle_id(
        self,
        vehicle_id: str
    ) -> list[Reservation]:


        models = (
            self.db.query(ReservationModel)
            .filter(
                ReservationModel.vehicle_id == vehicle_id,
                ReservationModel.status == ReservationStatus.ACTIVE
            )
            .all()
        )


        return [
            ReservationMapper.to_domain(model)
            for model in models
        ]

    def update(
        self,
        reservation: Reservation,
    ) -> Reservation:

        model = (
            self.db.query(ReservationModel)
            .filter(
                ReservationModel.id == reservation.id
            )
            .first()
        )

        if not model:
            raise ReservationNotFound()

        ReservationMapper.update_model(
            model=model,
            entity=reservation,
        )

        self.db.flush()

        return ReservationMapper.to_domain(model)