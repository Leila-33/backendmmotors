from modules.applications.domain.enums import EventType
import logging

logger = logging.getLogger(__name__)

class ExpireQuotesUseCase:
    """
    Expire automatiquement les devis dont la date de validité est dépassée
    et enregistre chaque expiration dans l'historique des événements.
    """
    def __init__(
        self,
        quote_repository,
        event_service,
        unit_of_work,
    ):
        self.quote_repository = quote_repository
        self.event_service = event_service
        self.uow = unit_of_work


    def execute(self):

        try:
            logger.info(
    "Début expiration automatique des devis"
)
            quotes = (
                self.quote_repository
                .find_quotes_to_expire()
            )


            for quote in quotes:

                old_status = quote.status


                quote.expire()


                self.quote_repository.update(
                    quote
                )


                self.event_service.log(
                    type=EventType.QUOTE_EXPIRED,
                    message="Devis expiré automatiquement",
                    quote_id=quote.id,
                    vehicle_id=quote.lead.vehicle.id,
                    user_id=None,
                    event_metadata={
                        "old_status": old_status.value,
                        "new_status": quote.status.value,
                        "expiration_date": (
                            quote.expired_at.isoformat()
                            if quote.expired_at
                            else None
                        ),
                    }
                )


            self.uow.commit()

            logger.info(
    "Expiration devis terminée",
    extra={
        "expired_count": len(quotes)
    }
)

        except Exception:

            self.uow.rollback()

            logger.exception(
    "Erreur expiration automatique devis"
)
            raise