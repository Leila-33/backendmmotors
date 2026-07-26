from modules.test_drives.api.schemas import MyTestDriveResponse

class MyTestDriveMapper:

    @staticmethod
    def to_response(model):

        return MyTestDriveResponse(

            id=model.id,

            vehicle_id=model.vehicle_id,

            vehicle_name=(
                f"{model.vehicle.brand} {model.vehicle.model}"
                if model.vehicle
                else ""
            ),

            appointment_date=model.appointment_date,

            status=model.status,

            comment=model.comment,
        )