from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import joinedload
from sqlalchemy import func
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
        date
    ):

        if isinstance(date, str):
            day_start = datetime.fromisoformat(date)

        elif isinstance(date, datetime):
            day_start = date

        else:
            raise ValueError(
                "Invalid date format"
            )


        day_start = day_start.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=timezone.utc
        )


        now = datetime.now(timezone.utc)

        day_end = (
            day_start + timedelta(days=1)
        )


        booked = (
            self.session.query(TestDriveModel)
            .filter(
                TestDriveModel.vehicle_id == vehicle_id,
                TestDriveModel.appointment_date >= day_start,
                TestDriveModel.appointment_date < day_end
            )
            .all()
        )


        booked_hours = {
            b.appointment_date.hour
            for b in booked
        }


        available = []

        for hour in range(9, 18):

            if day_start.date() == now.date():

                if hour <= now.hour:
                    continue


            if hour in booked_hours:
                continue


            slot = day_start.replace(
                hour=hour
            )

            available.append(
                slot.isoformat()
            )


        return {
            "date": day_start.date().isoformat(),
            "timezone": "UTC",
            "available_slots": available
        }


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


    # =========================
    # GET ALL
    # =========================
    def get_all_admin(
        self,
        status: str | None = None,
        search: str | None = None,
        page: int = 1,
        limit: int = 20
    ):

        query = (
            self.session.query(TestDriveModel)
            .options(
                joinedload(TestDriveModel.user),
                joinedload(TestDriveModel.vehicle),
            )
        )

        if status:
            query = query.filter(
                TestDriveModel.status == status
            )

        if search:
            query = query.filter(
                (
                    UserModel.first_name.ilike(f"%{search}%")
                )
                |
                (
                    UserModel.last_name.ilike(f"%{search}%")
                )
                |
                (
                    VehicleModel.brand.ilike(f"%{search}%")
                )
                |
                (
                    VehicleModel.model.ilike(f"%{search}%")
                )
            )

        total = query.with_entities(
            func.count(TestDriveModel.id)
        ).scalar()

        items = (
            query
            .order_by(TestDriveModel.appointment_date.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return PaginatedResult(
            items=items,
            total=total,
            page=page,
            limit=limit
        )


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


    # =========================
    # BY USER
    # =========================
    def get_by_user_id(
        self,
        user_id: str
    ):

        return (
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