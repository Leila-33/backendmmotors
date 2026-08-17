from dataclasses import dataclass


@dataclass
class GetCustomerQuoteDetailDTO:

    quote_id: str
    customer_id: str