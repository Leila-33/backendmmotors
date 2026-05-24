from modules.test_drives.domain.repositories.test_drive_repository import (
    TestDriveRepository,
)

from modules.test_drives.infrastructure.db.test_drive_model import (
    TestDriveModel,
)
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import joinedload

class TestDriveRepositorySQL(
    TestDriveRepository
):

    def __init__(self, session):
        self.session = session

    def create(self, test_drive):

        model = TestDriveModel(
            id=test_drive.id,
            user_id=test_drive.user_id,
            vehicle_id=test_drive.vehicle_id,
            appointment_date=test_drive.appointment_date,
            status=test_drive.status.value,
            comment=test_drive.comment,
            created_at=test_drive.created_at
        )

        self.session.add(model)

        return model


    def find_conflicting_slot(self, vehicle_id, appointment_date):

        start = appointment_date
        end = appointment_date + timedelta(hours=1)

        return (
            self.session.query(TestDriveModel)
            .filter(
                TestDriveModel.vehicle_id == vehicle_id,
                TestDriveModel.appointment_date < end,
                (TestDriveModel.appointment_date + timedelta(hours=1)) > start
            )
            .first()
        )

    def commit(self):
        self.session.commit()








    def get_day_availability(self, vehicle_id: str, date):

        # =========================
        # NORMALIZE INPUT
        # =========================
        if isinstance(date, str):
            day_start = datetime.fromisoformat(date)
        elif isinstance(date, datetime):
            day_start = date
        else:
            raise ValueError("Invalid date format")

        # =========================
        # FORCE UTC SAFE BASE
        # =========================
        day_start = day_start.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=timezone.utc
        )

        now = datetime.now(timezone.utc)

        day_end = day_start + timedelta(days=1)

        # =========================
        # GET BOOKINGS
        # =========================
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
            b.appointment_date.hour for b in booked
        }

        # =========================
        # SLOT GENERATION
        # =========================
        all_slots = list(range(9, 18))

        available = []

        for h in all_slots:

            # =========================
            # TODAY FILTER (UTC SAFE)
            # =========================
            if day_start.date() == now.date():

                if h <= now.hour:
                    continue

            # =========================
            # BOOKED FILTER
            # =========================
            if h in booked_hours:
                continue

            # =========================
            # BUILD FULL UTC ISO
            # =========================
            slot_datetime = day_start.replace(hour=h)

            available.append(
                slot_datetime.isoformat()
            )

        return {
            "date": day_start.date().isoformat(),
            "timezone": "UTC",
            "available_slots": available
        }
        
    def count_pending(self):

        return (
            self.session.query(TestDriveModel)
            .filter(TestDriveModel.status == "pending")
            .count()
        )
    
    def get_all(self):

        return (
            self.session.query(TestDriveModel)
            .order_by(TestDriveModel.created_at.desc())
            .all()
        )
    
    def get_by_id(self, test_drive_id: str):

        return (
            self.session.query(TestDriveModel)
            .filter(
                TestDriveModel.id == test_drive_id
            )
            .first()
        )


    def update(self, test_drive):

        self.session.add(test_drive)

    def get_full_by_id(self, test_drive_id: str):

        return (
            self.session.query(TestDriveModel)
            .filter(TestDriveModel.id == test_drive_id)
            .join(TestDriveModel.user)
            .join(TestDriveModel.vehicle)
            .outerjoin(TestDriveModel.events)
            .options(
                joinedload(TestDriveModel.user),
                joinedload(TestDriveModel.vehicle),
                joinedload(TestDriveModel.events)
            )
            .first()
        )
    
    def get_by_user_id(self, user_id: str):

        return (
            self.session.query(TestDriveModel)
            .filter(TestDriveModel.user_id == user_id)
            .join(TestDriveModel.vehicle)
            .all()
        )