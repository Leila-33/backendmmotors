from dataclasses import dataclass


@dataclass
class GetExistingTestDriveDTO:

    # =====================================================
    # UTILISATEUR CONNECTÉ
    # =====================================================

    user_id: int

    # =====================================================
    # VÉHICULE
    # =====================================================

    vehicle_id: int