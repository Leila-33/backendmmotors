class SearchVehicles:

    def __init__(self, vehicle_repository):
        self.vehicle_repository = vehicle_repository

    def execute(self, filters: dict):
        return self.vehicle_repository.search(filters)