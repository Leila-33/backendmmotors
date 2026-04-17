class GetApplicationStatus:

    def __init__(self, application_repo, vehicle_repo):
        self.application_repo = application_repo
        self.vehicle_repo = vehicle_repo

    def execute(self, application_id: str, user_id: str):

        # 🔹 1. Récupérer application
        application = self.application_repo.get_by_id(application_id)

        if not application:
            raise Exception("APPLICATION_NOT_FOUND")

        # 🔐 sécurité : vérifier propriétaire
        if application.user_id != user_id:
            raise Exception("FORBIDDEN")

        # 🔹 2. Récupérer véhicule
        vehicle = self.vehicle_repo.get_by_id(application.vehicle_id)

        # 🔹 3. Format dates
        created_at = (
            application.created_at.strftime("%Y-%m-%d")
            if application.created_at else None
        )

        submitted_at = (
            application.submitted_at.strftime("%Y-%m-%d")
            if application.submitted_at else None
        )

        # 🔹 4. Response
        return {
            "id": application.id,
            "status": application.status.value,
            "createdAt": created_at,
            "submittedAt": submitted_at,
            "project": {
                "type": vehicle.type,  # 🔥 ici
                "vehicle": {
                    "brand": vehicle.brand,
                    "model": vehicle.model
                }
            }
        }