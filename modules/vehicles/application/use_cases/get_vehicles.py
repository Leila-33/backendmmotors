from modules.vehicles.application.use_cases.admin.create_vehicle import VehicleMapper

class GetVehiclesForClientUseCase:

    def __init__(self, repo):
        self.repo = repo

    def execute(self, filters):

        filters.is_available = True  # force business rule

        vehicles, total = self.repo.search(filters)

        return {
            "items": [VehicleMapper.to_response(v) for v in vehicles],
            "total": total,
            "page": filters.page,
            "size": filters.size
        }
    
class GetVehiclesForAdminUseCase:

    def __init__(self, repo):
        self.repo = repo

    def execute(self, filters):

        vehicles, total = self.repo.search(filters)

        return {
            "items": [VehicleMapper.to_response(v) for v in vehicles],
            "total": total,
            "page": filters.page,
            "size": filters.size
        }