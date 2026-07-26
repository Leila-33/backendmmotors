from modules.test_drives.api.schemas import TestDriveDetailsAdminResponse


class TestDriveDetailAdminMapper:

    @staticmethod
    def to_response(test_drive) -> TestDriveDetailsAdminResponse:

        return TestDriveDetailsAdminResponse(
            id=test_drive.id,

            # =========================
            # USER
            # =========================
            user_name=(
                f"{test_drive.user.first_name} "
                f"{test_drive.user.last_name}"
            ),
            user_email=test_drive.user.email,

            # =========================
            # VEHICLE
            # =========================
            vehicle_name=(
                f"{test_drive.vehicle.brand} "
                f"{test_drive.vehicle.model}"
            ),
            vehicle_price=test_drive.vehicle.price,
            vehicle_license_plate=test_drive.vehicle.license_plate,

            # =========================
            # APPOINTMENT
            # =========================
            appointment_date=test_drive.appointment_date,
            status=test_drive.status.value,
            comment=test_drive.comment,

            # =========================
            # EVENTS TIMELINE
            # =========================
            events=[
                {
                    "id": event.id,
                    "type": (
                        event.type.value
                        if hasattr(event.type, "value")
                        else event.type
                    ),
                    "message": event.message,
                    "created_at": event.created_at,
                }
                for event in test_drive.events
            ]
        )