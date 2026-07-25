from modules.test_drives.api.schemas import TestDriveFullResponse

class TestDriveFullMapper:

    @staticmethod
    def to_response(
        model
    ) -> TestDriveFullResponse:

        return TestDriveFullResponse(

            id=model.id,

            # =========================
            # USER
            # =========================
            user={
                "id": model.user.id,
                "first_name": model.user.first_name,
                "last_name": model.user.last_name,
                "email": model.user.email,
            }
            if model.user
            else None,


            # =========================
            # VEHICLE
            # =========================
            vehicle={
                "id": model.vehicle.id,
                "brand": model.vehicle.brand,
                "model": model.vehicle.model,
                "year": model.vehicle.year,
                "images": model.vehicle.images or [],
            }
            if model.vehicle
            else None,


            # =========================
            # APPOINTMENT
            # =========================
            appointment_date=(
                model.appointment_date
            ),

            status=(
                model.status
            ),

            comment=(
                model.comment
            ),


            # =========================
            # EVENTS
            # =========================
            events=[
                {
                    "id": event.id,
                    "type": event.type,
                    "message": event.message,
                    "created_at": event.created_at,
                }
                for event in (model.events or [])
            ],


            created_at=(
                model.created_at
            )
        )