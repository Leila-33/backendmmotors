class CustomerAccountService:

    def __init__(
        self,
        user_creation_service,
        activation_token_service,
        lead_repository,
    ):
        self.user_creation_service = user_creation_service
        self.activation_token_service = activation_token_service
        self.lead_repository = lead_repository



    def ensure_account(
        self,
        lead,
        quote_id: str | None = None,
    ):


        # =========================
        # CREATE OR GET USER
        # =========================

        user, created = (
            self.user_creation_service
            .create_client(
                first_name=lead.first_name,
                last_name=lead.last_name,
                email=lead.email,
            )
        )
        self.lead_repository.attach_user(
    lead_id=lead.id,
    user_id=user.id,
)


        token = None


        # =========================
        # ACTIVATION TOKEN
        # =========================

        if created:

            token = (
                self.activation_token_service
                .create(
                    user_id=user.id,
                    quote_id=quote_id,
                )
            )


        return {

            "user": user,

            "created": created,

            "token": token,
        }