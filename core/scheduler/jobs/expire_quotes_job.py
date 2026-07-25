from modules.dependencies.dependencies import (
    get_quote_repository,
)

from core.database.dependencies import (
    get_unit_of_work,
)

from modules.quotes.application.services.quote_expiration_service import (
    QuoteExpirationService,
)


def run_expire_quotes():

    quote_repository = (
        get_quote_repository()
    )

    unit_of_work = (
        get_unit_of_work()
    )

    service = QuoteExpirationService()


    try:

        quotes = (
            quote_repository
            .find_quotes_to_expire()
        )


        for quote in quotes:

            if service.expire(quote):

                quote_repository.update(
                    quote
                )


        unit_of_work.commit()


    except Exception:

        unit_of_work.rollback()

        raise