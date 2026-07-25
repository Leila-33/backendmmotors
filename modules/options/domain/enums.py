from enum import Enum

class OptionType(str, Enum):
    INCLUDED = "included"
    CUSTOM = "custom"


class BillingType(str, Enum):
    FIXED = "fixed"
    DAILY = "daily"