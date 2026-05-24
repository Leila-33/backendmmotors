# app/infrastructure/db/import_models.py

# Users
from modules.auth.infrastructure.db.user_model import UserModel

# Auth (refresh + blacklist)
from modules.auth.infrastructure.db.refresh_model import RefreshTokenModel
from modules.auth.infrastructure.db.token_blacklist_model import TokenBlacklistModel

# Vehicles
from modules.vehicles.infrastructure.db.vehicle_model import VehicleModel
from modules.vehicles.infrastructure.db.vehicle_option_model import VehicleOptionModel

# Applications
from modules.applications.infrastructure.db.application_model import ApplicationModel
from modules.applications.infrastructure.db.application_option_model import ApplicationOptionModel
from modules.applications.infrastructure.db.document_model import DocumentModel
from modules.applications.infrastructure.db.event_model import EventModel
from modules.applications.infrastructure.db.application_financing_model import ApplicationFinancingModel
from modules.applications.infrastructure.db.application_trade_in_model import ApplicationTradeInModel
# Options
from modules.options.infrastructure.db.option_model import OptionModel

# Notifications / Events
from modules.notifications.infrastructure.db.notification_model import NotificationModel

# Test_drives
from modules.test_drives.infrastructure.db.test_drive_model import TestDriveModel


# Reservations
from modules.reservations.infrastructure.db.reservation_model import ReservationModel

#Favorites
from modules.favorites.infrastructure.db.favorite_model import FavoriteModel