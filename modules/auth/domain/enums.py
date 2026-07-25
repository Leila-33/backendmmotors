from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    CLIENT = "client"
    SAV_AGENT = "sav_agent"
    SALES_AGENT = "sales_agent"
