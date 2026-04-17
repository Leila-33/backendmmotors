from infrastructure.db.session import SessionLocal
from modules.applications.infrastructure.db.models import ApplicationEventModel
from modules.applications.domain.entities.application_event import ApplicationEvent


class ApplicationEventRepositorySQL:

    # =========================
    # SAVE EVENT
    # =========================
    def save(self, event: ApplicationEvent):
        db = SessionLocal()
        try:
            model = ApplicationEventModel(
                id=event.id,
                application_id=event.application_id,
                type=event.type,
                message=event.message,
                created_at=event.created_at
            )

            db.add(model)
            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    # =========================
    # GET BY APPLICATION
    # =========================
    def get_by_application_id(self, application_id: str):
        db = SessionLocal()
        try:
            results = db.query(ApplicationEventModel)\
                .filter(ApplicationEventModel.application_id == application_id)\
                .order_by(ApplicationEventModel.created_at.asc())\
                .all()

            return [
                ApplicationEvent(
                    id=e.id,
                    application_id=e.application_id,
                    type=e.type,
                    message=e.message,
                    created_at=e.created_at
                )
                for e in results
            ]

        finally:
            db.close()