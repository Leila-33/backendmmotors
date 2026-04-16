from sqlalchemy import Column, String, Float, Enum as SqlEnum
from sqlalchemy.dialects.postgresql import ARRAY

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

    document_ids = Column(ARRAY(String))


class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True)

    application_id = Column(String)

    type = Column(String)

    file_url = Column(String)

    status = Column(String)

    comment = Column(String)