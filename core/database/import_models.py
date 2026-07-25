# app/infrastructure/db/import_models.py

# Users
from modules.auth.infrastructure.db.user_model import UserModel

# Auth (refresh + blacklist)
from modules.auth.infrastructure.db.refresh_model import RefreshTokenModel
from modules.auth.infrastructure.db.token_blacklist_model import TokenBlacklistModel
from modules.auth.infrastructure.db.user_activation_token_model import UserActivationTokenModel

# Options
from modules.options.infrastructure.db.option_model import OptionModel

# Vehicles
from modules.vehicles.infrastructure.db.vehicle_model import VehicleModel
from modules.vehicles.infrastructure.db.vehicle_option_model import VehicleOptionModel

# Reconditioning
from modules.reconditionings.infrastructure.db.reconditioning_model import ReconditioningModel

# Inspection
from modules.inspections.infrastructure.db.inspection_model import InspectionModel

# Warranties
from modules.warranties.infrastructure.db.vehicle_warranty_model import VehicleWarrantyModel
from modules.warranties.infrastructure.db.warranty_plan_model import WarrantyPlanModel

# Applications
from modules.applications.infrastructure.db.application_model import ApplicationModel
from modules.applications.infrastructure.db.application_option_model import ApplicationOptionModel
from modules.applications.infrastructure.db.document_model import DocumentModel
from modules.applications.infrastructure.db.event_model import EventModel
from modules.applications.infrastructure.db.application_financing_model import ApplicationFinancingModel
from modules.applications.infrastructure.db.application_trade_in_model import ApplicationTradeInModel

# Notifications / Events
from modules.notifications.infrastructure.db.notification_model import NotificationModel

# Test_drives
from modules.test_drives.infrastructure.db.test_drive_model import TestDriveModel


# Reservations
from modules.reservations.infrastructure.db.reservation_model import ReservationModel

# Favorites
from modules.favorites.infrastructure.db.favorite_model import FavoriteModel

# Financing
from modules.financing.infrastructure.db.financing_contract_model import FinancingContractModel
from modules.financing.infrastructure.db.installment_model import InstallmentPaymentModel

# Payments
from modules.payments.infrastructure.db.payment_model import PaymentModel

# Sav
from modules.sav.infrastructure.db.support_ticket_model import SupportTicketModel
from modules.sav.infrastructure.db.ticket_message_model import TicketMessageModel
from modules.sav.infrastructure.db.ticket_read_state_model import TicketReadStateModel

# Leads
from modules.leads.infrastructure.db.lead_model import LeadModel

# Quotes
from modules.quotes.infrastructure.db.quote_model import QuoteModel
from modules.quotes.infrastructure.db.quote_trade_in_model import QuoteTradeInModel