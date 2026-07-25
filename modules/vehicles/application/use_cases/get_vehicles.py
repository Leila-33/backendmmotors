from modules.vehicles.infrastructure.mappers.vehicle_mapper import VehicleMapper


class BaseGetVehiclesUseCase:

    def __init__(self, repo):
        self.repo = repo


    def _execute(self, filters):

        vehicles, total = self.repo.search(filters)

        return {
    "items": vehicles,
    "total": total,
    "page": filters.page,
    "size": filters.size
}



class GetVehiclesForClientUseCase(BaseGetVehiclesUseCase):

    def execute(self, filters):

        # =========================
        # BUSINESS RULE CLIENT
        # =========================

        filters.is_available = True

        return self._execute(filters)



class GetVehiclesForAdminUseCase(BaseGetVehiclesUseCase):

    def execute(self, filters):

        return self._execute(filters)