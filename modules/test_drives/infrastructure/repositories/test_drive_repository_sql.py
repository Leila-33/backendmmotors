from datetime import date, datetime, timedelta, timezone
from sqlalchemy.orm import joinedload
from sqlalchemy import func, or_
from modules.test_drives.domain.repositories.test_drive_repository import (
    TestDriveRepository
)
from modules.test_drives.infrastructure.db.test_drive_model import (
    TestDriveModel
)
from modules.test_drives.infrastructure.mappers.test_drive_mapper import (
    TestDriveMapper
)
from core.pagination.paginated_result import PaginatedResult
from modules.auth.infrastructure.db.user_model import UserModel
from modules.vehicles.infrastructure.db.vehicle_model import VehicleModel
from modules.test_drives.domain.enums import TestDriveStatus
from modules.test_drives.domain.entities.test_drive import TestDrive
from modules.test_drives.application.results.admin.get_test_drives_admin_result import (
    GetTestDrivesAdminResult,
    TestDriveAdminStats
)

class TestDriveRepositorySQL(TestDriveRepository):

    def __init__(
        self,
        session
    ):
        self.session = session


    # =========================
    # CREATE
    # =========================
    def create(
        self,
        test_drive
    ):

        model = TestDriveMapper.to_model(
            test_drive
        )

        self.session.add(model)

        return TestDriveMapper.to_domain(
            model
        )


    # =========================
    # CONFLICT SLOT
    # =========================
    def find_conflicting_slot(
        self,
        vehicle_id: str,
        appointment_date: datetime
    ):

        start = appointment_date
        end = appointment_date + timedelta(hours=1)

        return (
            self.session.query(TestDriveModel)
            .filter(
                TestDriveModel.vehicle_id == vehicle_id,
                TestDriveModel.appointment_date < end,
                TestDriveModel.appointment_date + timedelta(hours=1) > start
            )
            .first()
        )


    # =========================
    # DAY AVAILABILITY
    # =========================
    def get_day_availability(
        self,
        vehicle_id: str,
        selected_date: date,
    ):
        # =========================
        # DAY RANGE
        # =========================

        day_start = datetime.combine(
            selected_date,
            datetime.min.time(),
            tzinfo=timezone.utc,
        )

        day_end = day_start + timedelta(days=1)

        # =========================
        # CURRENT TIME
        # =========================

        now = datetime.now(timezone.utc)

        # =========================
        # BOOKED SLOTS
        # =========================

        booked = (
            self.session.query(TestDriveModel)
            .filter(
                TestDriveModel.vehicle_id == vehicle_id,
                TestDriveModel.appointment_date >= day_start,
                TestDriveModel.appointment_date < day_end,
            )
            .all()
        )

        booked_hours = {
            appointment.appointment_date.hour
            for appointment in booked
        }

        # =========================
        # AVAILABLE SLOTS
        # =========================

        available = []

        for hour in range(9, 18):

            # Pour aujourd'hui, ne proposer
            # que les créneaux futurs.
            if (
                selected_date == now.date()
                and hour <= now.hour
            ):
                continue

            if hour in booked_hours:
                continue

            slot = day_start.replace(
                hour=hour
            )

            available.append(
                slot.isoformat()
            )

        # =========================
        # RESULT
        # =========================

        return {
            "date": selected_date.isoformat(),
            "timezone": "UTC",
            "available_slots": available,
        }

    # =========================
    # GET ALL
    # =========================
    # =========================
    # GET BY ID
    # =========================
    def get_by_id(
        self,
        test_drive_id: str
    ):

        model = (
            self.session.query(TestDriveModel)
            .filter(
                TestDriveModel.id == test_drive_id
            )
            .first()
        )

        if not model:
            return None


        return TestDriveMapper.to_domain(
            model
        )
    # =========================
    # BY USER
    # =========================

    def get_by_user_id(
        self,
        user_id: str,
    ) -> list[TestDrive]:

        models = (
            self.session.query(TestDriveModel)
            .options(
                joinedload(TestDriveModel.vehicle)
            )
            .filter(
                TestDriveModel.user_id == user_id
            )
            .order_by(
                TestDriveModel.created_at.desc()
            )
            .all()
        )

        return [
            TestDriveMapper.to_domain(model)
            for model in models
        ]

    # =========================
    # FULL DETAILS
    # =========================
    def get_full_by_id(
        self,
        test_drive_id: str
    ):

        return (
            self.session.query(TestDriveModel)
            .filter(
                TestDriveModel.id == test_drive_id
            )
            .options(
                joinedload(TestDriveModel.user),
                joinedload(TestDriveModel.vehicle),
                joinedload(TestDriveModel.events)
            )
            .first()
        )



    def get_all_admin(
        self,
        status: TestDriveStatus | None = None,
        search: str | None = None,
        date: str | None = None,
        sort_by: str = "appointment_date",
        sort_order: str = "asc",
        page: int = 1,
        limit: int = 20,
    ) -> GetTestDrivesAdminResult:

        # =========================
        # REQUÊTE PRINCIPALE
        # =========================

        query = (
            self.session.query(TestDriveModel)
            .join(
                UserModel,
                UserModel.id == TestDriveModel.user_id,
            )
            .join(
                VehicleModel,
                VehicleModel.id == TestDriveModel.vehicle_id,
            )
            .options(
                joinedload(TestDriveModel.user),
                joinedload(TestDriveModel.vehicle),
            )
        )

        # =========================
        # FILTRE STATUT
        # =========================

        if status is not None:
            query = query.filter(
                TestDriveModel.status == status
            )

        # =========================
        # RECHERCHE
        # =========================

        if search:
            search_pattern = f"%{search}%"

            query = query.filter(
                or_(
                    UserModel.first_name.ilike(search_pattern),
                    UserModel.last_name.ilike(search_pattern),
                    VehicleModel.brand.ilike(search_pattern),
                    VehicleModel.model.ilike(search_pattern),
                )
            )

        # =========================
        # FILTRE DATE
        # =========================

        if date:
            now = datetime.now(timezone.utc)

            if date == "today":
                start_date = now.replace(
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                )

                end_date = start_date + timedelta(days=1)

            elif date == "week":
                start_date = (
                    now
                    - timedelta(days=now.weekday())
                ).replace(
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                )

                end_date = start_date + timedelta(days=7)

            elif date == "month":
                start_date = now.replace(
                    day=1,
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                )

                if start_date.month == 12:
                    end_date = start_date.replace(
                        year=start_date.year + 1,
                        month=1,
                    )
                else:
                    end_date = start_date.replace(
                        month=start_date.month + 1,
                    )

            else:
                start_date = None
                end_date = None

            if start_date and end_date:
                query = query.filter(
                    TestDriveModel.appointment_date >= start_date,
                    TestDriveModel.appointment_date < end_date,
                )

        # =========================
        # TOTAL
        # =========================

        total = query.count()

        # =========================
        # STATISTIQUES
        #
        # Les statistiques sont calculées
        # avant la pagination.
        # =========================

        stats_query = (
            self.session.query(TestDriveModel.status)
            .join(
                UserModel,
                UserModel.id == TestDriveModel.user_id,
            )
            .join(
                VehicleModel,
                VehicleModel.id == TestDriveModel.vehicle_id,
            )
        )

        # Même filtre statut
        if status is not None:
            stats_query = stats_query.filter(
                TestDriveModel.status == status
            )

        # Même recherche
        if search:
            search_pattern = f"%{search}%"

            stats_query = stats_query.filter(
                or_(
                    UserModel.first_name.ilike(search_pattern),
                    UserModel.last_name.ilike(search_pattern),
                    VehicleModel.brand.ilike(search_pattern),
                    VehicleModel.model.ilike(search_pattern),
                )
            )

        # Même filtre date
        if date:
            now = datetime.now(timezone.utc)

            if date == "today":
                start_date = now.replace(
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                )

                end_date = start_date + timedelta(days=1)

            elif date == "week":
                start_date = (
                    now
                    - timedelta(days=now.weekday())
                ).replace(
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                )

                end_date = start_date + timedelta(days=7)

            elif date == "month":
                start_date = now.replace(
                    day=1,
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                )

                if start_date.month == 12:
                    end_date = start_date.replace(
                        year=start_date.year + 1,
                        month=1,
                    )
                else:
                    end_date = start_date.replace(
                        month=start_date.month + 1,
                    )

            else:
                start_date = None
                end_date = None

            if start_date and end_date:
                stats_query = stats_query.filter(
                    TestDriveModel.appointment_date >= start_date,
                    TestDriveModel.appointment_date < end_date,
                )

        # =========================
        # STATISTIQUES
        # =========================

        stats_rows = (
            query
            .with_entities(
                TestDriveModel.status
            )
            .group_by(
                TestDriveModel.status
            )
            .all()
        )

        stats = {
            "pending": 0,
            "confirmed": 0,
            "completed": 0,
            "cancelled": 0,
        }

        for row in stats_rows:

            current_status = row[0]

            if current_status == TestDriveStatus.PENDING:

                stats["pending"] += 1

            elif current_status == TestDriveStatus.CONFIRMED:

                stats["confirmed"] += 1

            elif current_status == TestDriveStatus.COMPLETED:

                stats["completed"] += 1

            elif current_status in (
                TestDriveStatus.CANCELLED,
                TestDriveStatus.REJECTED,
            ):

                stats["cancelled"] += 1
        # =========================
        # TRI
        # =========================

        sort_columns = {
            "appointment_date": TestDriveModel.appointment_date,
            "created_at": TestDriveModel.created_at,
        }

        # On utilise uniquement des colonnes
        # explicitement autorisées.
        sort_column = sort_columns.get(
            sort_by,
            TestDriveModel.appointment_date,
        )

        if sort_order == "desc":
            sort_column = sort_column.desc()
        else:
            sort_column = sort_column.asc()

        # =========================
        # PAGINATION
        # =========================

        models = (
            query
            .order_by(sort_column)
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        # =========================
        # CONVERSION ORM → DOMAINE
        # =========================

        items = [
            TestDriveMapper.to_domain(model)
            for model in models
        ]

        # =========================
        # RÉSULTAT
        # =========================

        return GetTestDrivesAdminResult(
            pagination=PaginatedResult(
                items=items,
                total=total,
                page=page,
                limit=limit,
            ),
            stats=TestDriveAdminStats(
                pending=stats["pending"],
                confirmed=stats["confirmed"],
                completed=stats["completed"],
                cancelled=stats["cancelled"],
            ),
        )

    # =========================
    # UPDATE
    # =========================
    def update(
        self,
        test_drive
    ):

        model = (
            self.session.query(TestDriveModel)
            .filter(
                TestDriveModel.id == test_drive.id
            )
            .first()
        )


        if not model:
            return None


        TestDriveMapper.update_model(
            model,
            test_drive
        )


        return TestDriveMapper.to_domain(
            model
        )



    # =========================
    # COUNT PENDING
    # =========================
    def count_pending(self):

        return (
            self.session
            .query(TestDriveModel)
            .filter(
                TestDriveModel.status == TestDriveStatus.PENDING
            )
            .count()
        )