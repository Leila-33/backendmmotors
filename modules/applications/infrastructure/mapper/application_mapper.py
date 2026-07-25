from modules.applications.domain.entities.application import Application

class ApplicationMapper:


    @staticmethod
    def to_dict(
        application: Application
    ):

        return {

            "id": application.id,

            "quote_id": application.quote_id,

            "user_id": application.user_id,

            "vehicle_id": application.vehicle_id,

            "first_name": application.first_name,

            "last_name": application.last_name,

            "email": application.email,

            "phone": application.phone,

            "status": application.status,

            "created_at": application.created_at,

            "discount": application.discount

        }