from modules.auth.domain.enums import UserRole
from modules.applications.api.schemas import (
    ApplicationListItemAdmin,
    ApplicationListItemUser,
    GetApplicationsResponse
)

class ApplicationListResponseFactory:


    # =========================
    # BUILD RESPONSE
    # =========================
    def build(
        self,
        result,
        role: UserRole
    ) -> GetApplicationsResponse:

        items = [
            self.build_item(
                item,
                role
            )
            for item in result.items
        ]

        return GetApplicationsResponse(
            items=items,
            page=result.page,
            limit=result.limit,
            total=result.total,
            pages=result.pages,
        )


    # =========================
    # BUILD ITEM
    # =========================
    def build_item(
        self,
        item,
        role: UserRole
    ):

        app = item.application


        base = {
            "id": app.id,

            "type": (
                app.vehicle.type
                if app.vehicle
                else None
            ),

            "vehicle": (
                f"{app.vehicle.brand} "
                f"{app.vehicle.model}"
                if app.vehicle
                else None
            ),

            "status": app.status,

            "submitted_at": (
                app.submitted_at
                if app.submitted_at
                else None
            ),
        }


        # =========================
        # ADMIN
        # =========================

        if role == UserRole.ADMIN:

            return ApplicationListItemAdmin(
                **base,

                client=(
                    f"{app.first_name or ''} "
                    f"{app.last_name or ''}"
                ).strip(),

                can_cancel=item.can_cancel,

                can_restore_cancelled=item.can_restore_cancelled,

                can_archive=item.can_archive,

                can_delete=item.can_delete,
            )


        # =========================
        # CLIENT
        # =========================

        return ApplicationListItemUser(
            **base,

            created_at=app.created_at,

            can_cancel=item.can_cancel,
        )