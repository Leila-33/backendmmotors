from enum import Enum

class LeadStatus(str, Enum):
    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    CONTACTED = "CONTACTED"
    QUOTE_SENT = "QUOTE_SENT"
    WON = "WON"
    LOST = "LOST"
