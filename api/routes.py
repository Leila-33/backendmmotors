from fastapi import APIRouter

from modules.auth.api.user_routes import router as auth_router
from modules.auth.api.admin_user_routes import router as admin_auth_router
from modules.vehicles.api.vehicle_routes import router as vehicle_router
from modules.vehicles.api.admin_vehicle_routes import router as admin_vehicle_router
from modules.reconditionings.api.admin_reconditioning_routes import router as admin_reconditioning_router
from modules.inspections.api.admin_inspection_routes import router as admin_inspection_router
from modules.warranties.api.admin_warranty_routes import router as admin_warranty_router
from modules.applications.api.application_routes import router as application_router
from modules.applications.api.admin_application_routes import router as admin_application_router
from modules.applications.api.admin_event_routes import router as admin_event_router
from modules.options.api.admin_option_routes import router as admin_option_router
from modules.storage.api.upload_routes import router as upload_router
from modules.reservations.api.reservation_routes import router as reservation_router
from modules.financing.api.trade_in_routes import router as trade_in_router
from modules.analytics.api.admin_analytics_routes import router as admin_analytics_router
from modules.analytics.api.admin_dashboard_routes import router as admin_dashboard_router
from modules.test_drives.api.test_drive_routes import router as test_drive_router
from modules.test_drives.api.admin_test_drive_routes import router as admin_test_drive_router
from modules.notifications.api.notification_routes import router as notification_router
from modules.notifications.api.notification_ws_router import router as notification_ws_router
from modules.favorites.api.favorites_routes import router as favorites_router
from modules.payments.api.payment_routes import router as payments_router
from modules.sav.api.support_ticket_routes import router as support_ticket_router
from modules.sav.api.support_ticket_ws_routes import router as support_ticket_ws_router
from modules.sav.api.agent_support_ticket_routes import router as agent_support_ticket_router
from modules.leads.api.lead_routes import router as lead_router
from modules.leads.api.agent_lead_routes import router as agent_lead_router
from modules.quotes.api.agent_quote_routes import router as agent_quote_router
from modules.quotes.api.quote_routes import router as quote_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(admin_auth_router, prefix="/admin/auth")
api_router.include_router(vehicle_router, prefix="/vehicles")
api_router.include_router(admin_vehicle_router, prefix="/admin/vehicles")
api_router.include_router(admin_reconditioning_router, prefix="/admin/reconditionings")
api_router.include_router(admin_inspection_router, prefix="/admin/inspections")
api_router.include_router(application_router, prefix="/applications")
api_router.include_router(admin_option_router, prefix="/admin/options")
api_router.include_router(admin_application_router, prefix="/admin/applications")
api_router.include_router(admin_event_router, prefix="/admin/events")
api_router.include_router(upload_router, prefix="/uploads")
api_router.include_router(reservation_router, prefix="/reservations")
api_router.include_router(trade_in_router, prefix="/trade-in")
api_router.include_router(admin_analytics_router, prefix="/admin/analytics")
api_router.include_router(admin_dashboard_router, prefix="/admin/dashboard")   
api_router.include_router(test_drive_router, prefix="/test-drives")   
api_router.include_router(admin_test_drive_router, prefix="/admin/test-drives")   
api_router.include_router(notification_router, prefix="/notifications")   
api_router.include_router(notification_ws_router, prefix="/ws/notifications")
api_router.include_router(favorites_router, prefix="/favorites")
api_router.include_router(admin_warranty_router, prefix="/admin/warranty-plans")
api_router.include_router(payments_router, prefix="/payments")
api_router.include_router(support_ticket_router, prefix="/support-tickets")
api_router.include_router(support_ticket_ws_router, prefix="/ws/support-tickets")
api_router.include_router(agent_support_ticket_router, prefix="/agent/support-tickets")
api_router.include_router(agent_lead_router, prefix="/agent/leads")
api_router.include_router(lead_router, prefix="/leads")
api_router.include_router(agent_quote_router, prefix="/agent/quotes")
api_router.include_router(quote_router, prefix="/quotes")