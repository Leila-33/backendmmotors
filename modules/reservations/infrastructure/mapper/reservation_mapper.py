from modules.reservations.domain.entities.reservation import Reservation
from modules.reservations.infrastructure.db.reservation_model import ReservationModel
from modules.reservations.api.schemas import ReservationResponse


class ReservationMapper:

    # =========================
    # MODEL -> DOMAIN
    # =========================
    @staticmethod
    def to_domain(
        model: ReservationModel
    ) -> Reservation:

        return Reservation(
            id=model.id,
            vehicle_id=model.vehicle_id,
            application_id=model.application_id,
            start_date=model.start_date,
            end_date=model.end_date,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


    # =========================
    # DOMAIN -> MODEL
    # =========================
    @staticmethod
    def to_model(
        entity: Reservation
    ) -> ReservationModel:

        return ReservationModel(
            id=entity.id,
            vehicle_id=entity.vehicle_id,
            application_id=entity.application_id,
            start_date=entity.start_date,
            end_date=entity.end_date,
            status=entity.status,
        )


    # =========================
    # UPDATE EXISTING MODEL
    # =========================
    @staticmethod
    def update_model(
        model: ReservationModel,
        entity: Reservation
    ) -> ReservationModel:

        model.vehicle_id = entity.vehicle_id
        model.application_id = entity.application_id
        model.start_date = entity.start_date
        model.end_date = entity.end_date
        model.status = entity.status

        return model


    # =========================
    # DOMAIN -> RESPONSE
    # =========================
    @staticmethod
    def to_response(
        reservation: Reservation
    ) -> ReservationResponse:

        return ReservationResponse(
            id=reservation.id,
            vehicle_id=reservation.vehicle_id,
            application_id=reservation.application_id,
            start_date=reservation.start_date,
            end_date=reservation.end_date,
            status=reservation.status,
            created_at=reservation.created_at,
            updated_at=reservation.updated_at,
        )