from modules.test_drives.api.schemas import (
    TestDriveDetailClientResponse
)


class TestDriveDetailClientMapper:


    @staticmethod
    def to_response(
        test_drive,
        events
    ):

        return TestDriveDetailClientResponse(

            id=test_drive.id,


            vehicle={
                "id": test_drive.vehicle.id,
                "brand": test_drive.vehicle.brand,
                "model": test_drive.vehicle.model,
                "images": test_drive.vehicle.images or [],
            },


            appointment_date=(
                test_drive.appointment_date
            ),


            status=(
                test_drive.status.value
            ),


            comment=test_drive.comment,


            user={
                "id": test_drive.user.id,
                "name": (
                    f"{test_drive.user.first_name} "
                    f"{test_drive.user.last_name}"
                ),
                "email": test_drive.user.email,
            },


            timeline=[

                {
                    "type": e.type.value
                    if hasattr(e.type, "value")
                    else e.type,

                    "message": e.message,

                    "date": e.created_at,

                    "metadata": e.event_metadata,

                }

                for e in events
            ]
        )