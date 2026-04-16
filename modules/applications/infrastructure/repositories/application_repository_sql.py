from infrastructure.db.session import SessionLocal
from modules.applications.infrastructure.db.models import ApplicationModel
from modules.applications.domain.entities.application import Application, ApplicationStatus


class ApplicationRepositorySQL:

    def get_by_id(self, application_id: str):
        db = SessionLocal()
        try:
            a = db.query(ApplicationModel).filter(
                ApplicationModel.id == application_id
            ).first()

            if not a:
                return None

            return Application(
                id=a.id,
                user_id=a.user_id,
                vehicle_id=a.vehicle_id,
                monthly_income=a.monthly_income,
                monthly_expenses=a.monthly_expenses,
                employment_status=a.employment_status,
                status=ApplicationStatus(a.status),
                document_ids=a.document_ids or []
            )

        finally:
            db.close()

    def save(self, application: Application):
        db = SessionLocal()
        try:
            model = ApplicationModel(
                id=application.id,
                user_id=application.user_id,
                vehicle_id=application.vehicle_id,
                monthly_income=application.monthly_income,
                monthly_expenses=application.monthly_expenses,
                employment_status=application.employment_status,
                status=application.status.value,
                document_ids=application.document_ids
            )

            db.add(model)
            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    def update(self, application: Application):
        db = SessionLocal()
        try:
            model = db.query(ApplicationModel).filter(
                ApplicationModel.id == application.id
            ).first()

            if not model:
                return None

            model.monthly_income = application.monthly_income
            model.monthly_expenses = application.monthly_expenses
            model.employment_status = application.employment_status
            model.status = application.status.value
            model.document_ids = application.document_ids

            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()