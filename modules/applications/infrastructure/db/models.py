from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from infrastructure.db.session import Base
from modules.applications.domain.entities.application import ApplicationStatus



class ApplicationModel(Base):
    __tablename__ = "applications"

    # =====================
    # IDENTIFIERS
    # =====================
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    vehicle_id = Column(String, ForeignKey("vehicles.id"))

    # =====================
    # SNAPSHOT USER (IMPORTANT)
    # =====================
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    birth_date = Column(DateTime)

    # =====================
    # FINANCIAL INFO
    # =====================
    monthly_income = Column(Float)
    monthly_expenses = Column(Float)
    employment_status = Column(String)

    # =====================
    # OPTIONS DOSSIER
    # =====================
    options_included = Column(String)  # JSON string ou ARRAY
    options_optional = Column(String)  # JSON string ou ARRAY
    options_selected = Column(String)   # idem

    # =====================
    # STATUS / DATES
    # =====================
    status = Column(SqlEnum(ApplicationStatus))

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    submitted_at = Column(DateTime, nullable=True)

    # =====================
    # RELATIONS
    # =====================
    user = relationship("UserModel")
    vehicle = relationship("VehicleModel")

    documents = relationship(
        "DocumentModel",
        back_populates="application",
        cascade="all, delete-orphan"
    )

    events = relationship(
        "ApplicationEventModel",
        back_populates="application",
        cascade="all, delete-orphan"
    )

class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True)

    application_id = Column(String, ForeignKey("applications.id"))

    type = Column(String)
    file_url = Column(String)

    status = Column(String)
    comment = Column(String)

    application = relationship("ApplicationModel", back_populates="documents")


class ApplicationEventModel(Base):
    __tablename__ = "application_events"

    id = Column(String, primary_key=True, index=True)

    application_id = Column(
        String,
        ForeignKey("applications.id"),
        nullable=False,
        index=True
    )

    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=True
    )

    type = Column(String, nullable=False)
    message = Column(String, nullable=False)

    created_at = Column(DateTime, nullable=False)

    # =====================
    # RELATIONS
    # =====================
    application = relationship("ApplicationModel", back_populates="events")
    user = relationship("UserModel")  # optionnel mais recommandé