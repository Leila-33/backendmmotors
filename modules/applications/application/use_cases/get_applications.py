from modules.auth.domain.enums import (
    UserRole,
)

from modules.applications.application.dtos.get_applications_dto import (
    GetApplicationsDTO,
)

from modules.applications.application.results.application_list_item_data import (
    ApplicationListItemData,
)

from modules.applications.application.services.restore_application_service import (
    RestoreApplicationService,
)

from modules.applications.domain.exceptions import (
    CannotRestoreApplication,
)
from modules.applications.domain.policies.process_application_policy import (
    ProcessApplicationPolicy,
)
from modules.applications.domain.policies.archive_application_policy import (
    ArchiveApplicationPolicy,
)
from modules.applications.domain.policies.cancel_application_policy import (
    CancelApplicationPolicy,
)
from modules.applications.domain.policies.restore_application_policy import (
    RestoreApplicationPolicy,
)
from modules.applications.domain.policies.soft_delete_application_policy import (
    SoftDeleteApplicationPolicy,
)

from modules.applications.domain.repositories.application_repository import (
    ApplicationRepository,
)

from core.pagination.paginated_result import PaginatedResult

class GetApplicationsUseCase:

    def __init__(
        self,
        application_repository: ApplicationRepository,
        restore_application_service: RestoreApplicationService,
    ):
        self.application_repository = application_repository
        self.restore_application_service = (
            restore_application_service
        )

    # =========================
    # EXECUTE
    # =========================
    def execute(
        self,
        dto: GetApplicationsDTO,
        role: UserRole,
        user_id: str,
    ):
        # =========================
        # SEARCH STRATEGY
        # =========================
        # Pour un client, la recherche porte sur le véhicule.
        # Pour un administrateur, elle porte sur l'utilisateur.
        search_field = (
            "vehicle"
            if role == UserRole.CLIENT
            else "user"
        )

        # =========================
        # FETCH
        # =========================
        applications, total = (
            self.application_repository.find_all(
                page=dto.page,
                limit=dto.limit,
                search=dto.search,
                search_field=search_field,
                status=dto.status,
                application_type=dto.application_type,
                sort=dto.sort,
                view_mode=dto.view_mode,
                user_id=user_id,
                role=role,
            )
        )

        # =========================
        # BUSINESS RULES
        # =========================
        items = []

        for application in applications:

            # -------------------------
            # Cancel
            # -------------------------
            can_cancel = (
                CancelApplicationPolicy.can_cancel(
                    application
                )
            )

            # -------------------------
            # Default admin actions
            # -------------------------
            can_process = False
            can_restore_cancelled = False
            can_delete = False
            can_archive = False

            # =========================
            # ADMIN RULES
            # =========================
            if role == UserRole.ADMIN:

                # -------------------------
                # Process
                # -------------------------
                # Le dossier peut être pris en charge
                # uniquement lorsque la policy l'autorise.
                can_process = (
                    ProcessApplicationPolicy.can_process(
                        application
                    )
                )

                # -------------------------
                # Restore cancelled
                # -------------------------
                try:
                    RestoreApplicationPolicy.validate(
                        application
                    )

                    self.restore_application_service.validate_rental(
                        application
                    )

                    can_restore_cancelled = True

                except CannotRestoreApplication:
                    can_restore_cancelled = False

                # -------------------------
                # Archive
                # -------------------------
                can_archive = (
                    ArchiveApplicationPolicy.can_archive(
                        application
                    )
                )

                # -------------------------
                # Soft delete
                # -------------------------
                can_delete = (
                    SoftDeleteApplicationPolicy.can_delete(
                        application
                    )
                )

            # =========================
            # LIST ITEM
            # =========================
            items.append(
                ApplicationListItemData(
                    application=application,

                    can_process=can_process,

                    can_cancel=can_cancel,

                    can_restore_cancelled=(
                        can_restore_cancelled
                    ),

                    can_archive=can_archive,

                    can_delete=can_delete,
                )
            )


        return PaginatedResult.create(
            items=items,
            page=dto.page,
            limit=dto.limit,
            total=total,
        )