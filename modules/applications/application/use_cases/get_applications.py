# =========================================
# app/application/usecases/get_applications_usecase.py
# =========================================

from modules.applications.api.schemas import (
    GetApplicationsDTO,
    ApplicationListItemAdmin,
    GetApplicationsResponse,
    ApplicationListItemUser
)



class GetApplicationsUseCase:

    def __init__(self, application_repository):
        self.application_repository = application_repository


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
        archived=dto.archived,
        user_id=user_id,   # 👈 IMPORTANT
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
            self._map_application(app, role)
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
    
    def _map_application(self, app, role: str):

        base = {
            "id": app.id,
            "type": app.vehicle.type,
            "vehicle": f"{app.vehicle.brand} {app.vehicle.model}",
            "status": app.status
        }

        # =========================
        # ADMIN VIEW
        # =========================
        if role == "admin":

            return ApplicationListItemAdmin(
                **base,
                client=f"{app.first_name} {app.last_name}",
                submitted_at=(
                    app.submitted_at.isoformat()
                    if app.submitted_at else None
                )
            )

        # =========================
        # USER VIEW
        # =========================
        return ApplicationListItemUser(
            **base,
            created_at=app.created_at.isoformat(),
            submitted_at=(
                app.submitted_at.isoformat()
                if app.submitted_at else None
            )
        )