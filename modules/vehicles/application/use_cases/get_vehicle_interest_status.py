from modules.vehicles.application.results.get_vehicle_interest_status_result import (
    GetVehicleInterestStatusResult,
)


class GetVehicleInterestStatusUseCase:
    """
    Détermine si un utilisateur est déjà intéressé par un véhicule
    et récupère, lorsqu'ils existent, le devis et le dossier associés.
    """
    def __init__(
        self,
        lead_repository,
        quote_repository,
        application_repository,
    ):
        self.lead_repository = lead_repository
        self.quote_repository = quote_repository
        self.application_repository = application_repository

    def execute(
        self,
        vehicle_id: str,
        user_id: str,
    ) -> GetVehicleInterestStatusResult:

        # =========================
        # LEAD
        # =========================

        lead = (
            self.lead_repository
            .find_active_by_user_and_vehicle(
                user_id=user_id,
                vehicle_id=vehicle_id,
            )
        )

        if lead is None:
            return GetVehicleInterestStatusResult(
                already_interested=False,
            )

        # =========================
        # QUOTE
        # =========================

        quote = (
            self.quote_repository
            .find_active_by_lead(
                lead.id
            )
        )

        if quote is None:
            return GetVehicleInterestStatusResult(
                already_interested=True,
            )

        # =========================
        # APPLICATION
        # =========================

        application = (
            self.application_repository
            .find_by_quote_id(
                quote.id
            )
        )

        # =========================
        # RESULT
        # =========================

        return GetVehicleInterestStatusResult(
            already_interested=True,
            quote_id=quote.id,
            quote_status=quote.status.value,
            application_id=(
                application.id
                if application
                else None
            ),
        )