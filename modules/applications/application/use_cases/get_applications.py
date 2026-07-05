from modules.applications.api.schemas import (
    GetApplicationsDTO,
    ApplicationListItemAdmin,
    GetApplicationsResponse,
    ApplicationListItemUser
)

from modules.applications.domain.policies.cancel_application_policy import CancelApplicationPolicy
from modules.applications.domain.policies.restore_application_policy import RestoreApplicationPolicy
class GetApplicationsUseCase:

    def __init__(self, application_repository, reservation_repository):
        self.application_repository = application_repository
        self.reservation_repository = reservation_repository


    def execute(
        self,
        dto: GetApplicationsDTO,
        role: str,
        user_id
    ):

        # =========================
        # SEARCH STRATEGY (ROLE-BASED)
        # =========================
        search_field = (
            "vehicle" if role == "client"
            else "user"
        )

        # =========================
        # FETCH DATA
        # =========================
        applications, total = self.application_repository.find_all(
        page=dto.page,
        limit=dto.limit,
        search=dto.search,
        search_field=search_field,
        status=dto.status,
        application_type=dto.application_type,
        sort=dto.sort,
        view_mode=dto.view_mode,
        user_id=user_id,
        role=role
    )
        # =========================
        # FILTER BY ROLE (SAFETY LAYER)
        # =========================
        if role == "client":
            applications = [
                app for app in applications
                if not app.is_archived
            ]

        # =========================
        # MAPPING
        # =========================
        items = [
            self._map_application(app, role, self.reservation_repository)
            for app in applications
        ]

        # =========================
        # PAGINATION
        # =========================
        pages = (total + dto.limit - 1) // dto.limit

        return GetApplicationsResponse(
            items=items,
            page=dto.page,
            limit=dto.limit,
            total=total,
            pages=pages
        )
    
    def _map_application(self, app, role: str, reservation_repository):

        submitted_at = (
            app.submitted_at.isoformat()
            if app.submitted_at else None
        )

        vehicle_name = (
            f"{app.vehicle.brand} {app.vehicle.model}"
        )

        base = {
            "id": app.id,
            "type": app.vehicle.type,
            "vehicle": vehicle_name,
            "status": app.status,
            "submitted_at": submitted_at,
        }

        # =========================
        # ADMIN VIEW
        # =========================
        if role == "admin":

            return ApplicationListItemAdmin(
                **base,
                client=f"{app.first_name} {app.last_name}",
                can_cancel=CancelApplicationPolicy.can_cancel(
                    app,
                    role
                ),
                can_restore_cancelled=RestoreApplicationPolicy.can_restore(
                    app,
                    reservation_repository
                )
            )

        # =========================
        # USER VIEW
        # =========================
        return ApplicationListItemUser(
            **base,
            created_at=app.created_at.isoformat(),
            can_cancel=CancelApplicationPolicy.can_cancel(
                app,
                role
            )
        )