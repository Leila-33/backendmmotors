def get_vehicle_repository():
    from modules.vehicles.infrastructure.repositories.vehicle_repository_sql import VehicleRepositorySQL
    return VehicleRepositorySQL()