from modules.test_drives.domain.repositories.test_drive_repository import (
    TestDriveRepository,
)

from modules.test_drives.infrastructure.db.test_drive_model import (
    TestDriveModel,
)
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import joinedload

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import joinedload

from modules.test_drives.domain.repositories.test_drive_repository import (
    TestDriveRepository
)
from modules.test_drives.infrastructure.models.test_drive_model import (
    TestDriveModel
)
from modules.test_drives.infrastructure.mapper.test_drive_mapper import (
    TestDriveMapper
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
            self.session.query(TestDriveModel)
            .filter(
                TestDriveModel.status == "pending"
            )
            .count()
        )


    # =========================
    # GET ALL
    # =========================
    def get_all(self):

        models = (
            self.session.query(TestDriveModel)
            .order_by(
                TestDriveModel.created_at.desc()
            )
            .all()
        )

        return [
            TestDriveMapper.to_domain(m)
            for m in models
        ]


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

        models = (
            self.session.query(TestDriveModel)
            .filter(
                TestDriveModel.user_id == user_id
            )
            .join(TestDriveModel.vehicle)
            .all()
        )

        return [
            TestDriveMapper.to_domain(m)
            for m in models
        ]