from fastapi import APIRouter

from modules.auth.api.user_routes import router as auth_router
from modules.auth.api.admin_user_routes import router as admin_auth_router
from modules.vehicles.api.vehicle_routes import router as vehicle_router
from modules.vehicles.api.admin_vehicle_routes import router as admin_vehicle_router

from modules.applications.api.application_routes import router as application_router
from modules.applications.api.admin_application_routes import router as admin_application_router
from modules.options.api.option_routes import router as option_router
from modules.storage.api.upload_routes import router as upload_router
from modules.reservations.api.reservation_routes import router as reservation_router
from modules.financing.api.trade_in_routes import router as trade_in_router
from modules.analytics.api.analytics_routes import router as analytics_router
from modules.dashboard.api.dashboard_routes import router as dashboard_router
from modules.test_drives.api.test_drive_routes import router as test_drive_router
from modules.test_drives.api.admin_test_drive_routes import router as admin_test_drive_router
from modules.notifications.api.notification_routes import router as notification_router
from modules.notifications.api.notifications_ws_router import router as notifications_ws_router
from modules.favorites.api.favorites_routes import router as favorites_router



api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(admin_auth_router, prefix="/admin/auth")
api_router.include_router(vehicle_router, prefix="/vehicles")
api_router.include_router(admin_vehicle_router, prefix="/admin/vehicles")
api_router.include_router(application_router, prefix="/applications")
api_router.include_router(option_router, prefix="/options")
api_router.include_router(admin_application_router, prefix="/admin/applications")
api_router.include_router(upload_router, prefix="/uploads")
api_router.include_router(reservation_router, prefix="/reservations")
api_router.include_router(trade_in_router, prefix="/trade-in")
api_router.include_router(analytics_router, prefix="/admin/analytics")
api_router.include_router(dashboard_router, prefix="/admin/dashboard")   
api_router.include_router(test_drive_router, prefix="/test-drives")   
api_router.include_router(admin_test_drive_router, prefix="/admin/test-drives")   
api_router.include_router(notification_router, prefix="/notifications")   
api_router.include_router(notifications_ws_router)
api_router.include_router(favorites_router, prefix="/favorites")