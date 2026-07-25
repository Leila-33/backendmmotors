class QuoteExpirationService:


    def expire(
        self,
        quote,
    ):

        if quote.is_expired():

            quote.expire()

            return True


        return False