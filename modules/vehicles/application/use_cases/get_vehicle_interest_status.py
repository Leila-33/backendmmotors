from modules.vehicles.api.schemas import VehicleInterestStatusResponse

class GetVehicleInterestStatus:


    def __init__(
        self,
        lead_repository,
        quote_repository,
        application_repository
    ):

        self.lead_repository = lead_repository
        self.quote_repository = quote_repository
        self.application_repository = application_repository



    def execute(
    self,
    vehicle_id: str,
    user_id: str
):

        lead = (
            self.lead_repository
            .find_active_by_user_and_vehicle(
                user_id=user_id,
                vehicle_id=vehicle_id
            )
        )


        if not lead:

            return VehicleInterestStatusResponse(
                already_interested=False
            )


        quote = (
            self.quote_repository
            .find_active_by_lead(
                lead.id
            )
        )


        if not quote:

            return VehicleInterestStatusResponse(
                already_interested=True
            )


        application = (
            self.application_repository
            .find_by_quote_id(
                quote.id
            )
        )


        return VehicleInterestStatusResponse(

            already_interested=True,

            quote_id=quote.id,

            quote_status=(
                quote.status.value
            ),

            application_id=(
                application.id
                if application
                else None
            )
        )