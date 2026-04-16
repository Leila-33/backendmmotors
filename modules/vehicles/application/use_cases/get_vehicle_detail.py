class GetVehicleDetail:

    def __init__(self, vehicle_repository):
        self.vehicle_repository = vehicle_repository

    def execute(self, vehicle_id: str):
        vehicle = self.vehicle_repository.get_by_id(vehicle_id)

        if not vehicle:
            raise Exception("VEHICLE_NOT_FOUND")

        return vehicle