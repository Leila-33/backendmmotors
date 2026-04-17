from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.db.session import Base


class ApplicationModel(Base):
    __tablename__ = "applications"

    id = Column(String, primary_key=True)

    user_id = Column(String)
    vehicle_id = Column(String)

    monthly_income = Column(Float)
    monthly_expenses = Column(Float)

    employment_status = Column(String)

    status = Column(String)

    # =========================
    # RELATIONS
    # =========================
    documents = relationship("DocumentModel", back_populates="application")
    events = relationship("ApplicationEventModel", back_populates="application")


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

    type = Column(String, nullable=False)
    message = Column(String, nullable=False)

    created_at = Column(DateTime, nullable=False)

    application = relationship("ApplicationModel", back_populates="events")