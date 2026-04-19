from infrastructure.db.session import SessionLocal
from modules.applications.infrastructure.db.models import ApplicationModel
from modules.clients.infrastructure.db.models import UserModel
from modules.vehicles.infrastructure.db.models import VehicleModel
from modules.applications.domain.entities.application import Application, ApplicationStatus
from sqlalchemy.orm import Session, joinedload
from infrastructure.db.session import SessionLocal
from sqlalchemy import or_

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









def search_admin(self, filters: dict):

    query = (
        self.db.query(ApplicationModel)
        .join(UserModel, ApplicationModel.user_id == UserModel.id)
        .join(VehicleModel, ApplicationModel.vehicle_id == VehicleModel.id)
        .options(
            joinedload(ApplicationModel.user),
            joinedload(ApplicationModel.vehicle),
            joinedload(ApplicationModel.events),
            joinedload(ApplicationModel.documents)  # ✅ AJOUT
        )
    )

    # =====================
    # FILTER STATUS
    # =====================
    if filters.get("status"):
        query = query.filter(ApplicationModel.status == filters["status"])

    # =====================
    # FILTER TYPE (achat/location)
    # =====================
    if filters.get("type"):
        query = query.filter(VehicleModel.type == filters["type"])

    # =====================
    # SEARCH CLIENT
    # =====================
    if filters.get("search"):
        search = f"%{filters['search']}%"
        query = query.filter(
            or_(
                UserModel.first_name.ilike(search),
                UserModel.last_name.ilike(search)
            )
        )

    # =====================
    # SORTING
    # =====================
    sort = filters.get("sort")

    if sort == "createdAt_asc":
        query = query.order_by(ApplicationModel.created_at.asc())
    elif sort == "createdAt_desc":
        query = query.order_by(ApplicationModel.created_at.desc())
    elif sort == "status":
        query = query.order_by(ApplicationModel.status.asc())
    else:
        query = query.order_by(ApplicationModel.created_at.desc())

    # =====================
    # PAGINATION
    # =====================
    page = filters.get("page", 1)
    limit = filters.get("limit", 10)

    total = query.count()

    results = (
        query
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    # =====================
    # FORMAT RESPONSE
    # =====================
    data = []

    for app in results:
        data.append({
            "id": app.id,
            "status": app.status,
            "createdAt": app.created_at.isoformat() if app.created_at else None,
            "submittedAt": app.submitted_at.isoformat() if app.submitted_at else None,

            # CLIENT
            "client": {
                "nom": app.user.last_name,
                "prenom": app.user.first_name,
                "phone": app.user.phone,
                "adresse": app.user.address,
                "birth_date": app.user.birth_date.isoformat() if app.user.birth_date else None
            },

            # VEHICLE
            "vehicle": {
                "brand": app.vehicle.brand,
                "model": app.vehicle.model,
                "type": app.vehicle.type
            },

            # ✅ DOCUMENTS
            "documents": [
                {
                    "id": doc.id,
                    "type": doc.type,
                    "file_url": doc.file_url,
                    "status": doc.status,
                    "comment": doc.comment
                }
                for doc in app.documents
            ],

            # EVENTS
            "events": [
                {
                    "type": e.type,
                    "message": e.message,
                    "date": e.created_at.isoformat(),
                    "user_id": e.user_id
                }
                for e in app.events
            ]
        })

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": data
    }


def get_detail_admin(self, application_id: str):

    app = (
        self.db.query(ApplicationModel)
        .options(
            joinedload(ApplicationModel.user),
            joinedload(ApplicationModel.vehicle),
            joinedload(ApplicationModel.documents),
            joinedload(ApplicationModel.events)
        )
        .filter(ApplicationModel.id == application_id)
        .first()
    )

    if not app:
        return None

    return {
        "id": app.id,
        "status": app.status,
        "createdAt": app.created_at.isoformat() if app.created_at else None,
        "submittedAt": app.submitted_at.isoformat() if app.submitted_at else None,

        # =====================
        # CLIENT
        # =====================
        "client": {
            "nom": app.user.last_name,
            "prenom": app.user.first_name,
            "phone": app.user.phone,
            "adresse": app.user.address,
            "birth_date": app.user.birth_date.isoformat() if app.user.birth_date else None
        },

        # =====================
        # VEHICLE
        # =====================
        "vehicle": {
            "id": app.vehicle.id,
            "brand": app.vehicle.brand,
            "model": app.vehicle.model,
            "type": app.vehicle.type
        },

        # =====================
        # OPTIONS INCLUSES
        # =====================
        "optionsIncluded": app.options_included or [],

        # =====================
        # OPTIONS CHOISIES
        # =====================
        "optionsSelected": app.options_selected or [],

        # =====================
        # DOCUMENTS
        # =====================
        "documents": [
            {
                "id": d.id,
                "type": d.type,
                "file_url": d.file_url,
                "status": d.status,
                "comment": d.comment
            }
            for d in app.documents
        ],

        # =====================
        # EVENTS
        # =====================
        "events": [
            {
                "type": e.type,
                "message": e.message,
                "date": e.created_at.isoformat(),
                "user_id": e.user_id
            }
            for e in app.events
        ]
    }


from sqlalchemy.orm import joinedload


def get_detail_application(self, application_id: str, user_id: str = None, is_admin: bool = False):

    query = (
        self.db.query(ApplicationModel)
        .options(
            joinedload(ApplicationModel.user),
            joinedload(ApplicationModel.vehicle),
            joinedload(ApplicationModel.documents),
            joinedload(ApplicationModel.events)
        )
    )

    # =========================
    # SECURITY (CLIENT ONLY)
    # =========================
    if not is_admin:
        query = query.filter(
            ApplicationModel.id == application_id,
            ApplicationModel.user_id == user_id
        )
    else:
        query = query.filter(ApplicationModel.id == application_id)

    app = query.first()

    if not app:
        return None

    # =========================
    # BASE RESPONSE (COMMON)
    # =========================
    response = {
        "id": app.id,
        "status": app.status,
        "createdAt": app.created_at.isoformat() if app.created_at else None,
        "submittedAt": app.submitted_at.isoformat() if app.submitted_at else None,

        # =====================
        # CLIENT
        # =====================
        "client": {
            "nom": app.user.last_name,
            "prenom": app.user.first_name,
            "phone": app.user.phone,
            "adresse": app.user.address,
            "birth_date": app.user.birth_date.isoformat() if app.user.birth_date else None
        },

        # =====================
        # VEHICLE
        # =====================
        "vehicle": {
            "id": app.vehicle.id,
            "brand": app.vehicle.brand,
            "model": app.vehicle.model,
            "type": app.vehicle.type
        },

        # =====================
        # OPTIONS
        # =====================
        "optionsIncluded": app.options_included or [],
        "optionsSelected": app.options_selected or [],

        # =====================
        # DOCUMENTS
        # =====================
        "documents": [
            {
                "id": d.id,
                "type": d.type,
                "file_url": d.file_url,
                "status": d.status,
                "comment": d.comment if is_admin else None
            }
            for d in app.documents
        ],

        # =====================
        # EVENTS
        # =====================
        "events": [
            {
                "type": e.type,
                "message": e.message,
                "date": e.created_at.isoformat(),
                "user_id": e.user_id if is_admin else None
            }
            for e in app.events
        ]
    }

    # =========================
    # ADMIN EXTRA DATA
    # =========================
    if not is_admin:
        response["optionsOptional"] = app.options_optional or []

    return response