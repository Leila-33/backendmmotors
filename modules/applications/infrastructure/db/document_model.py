from sqlalchemy import Column, String, Enum, ForeignKey
from sqlalchemy.orm import relationship

from modules.applications.domain.enums import DocumentType, DocumentStatus
from core.database.session import Base

class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True)

    application_id = Column(
        String,
        ForeignKey("applications.id"),
        nullable=False,
        index=True
    )

    type = Column(
        Enum(DocumentType),
        nullable=False
    )

    # 🔥 IMPORTANT
    s3_key = Column(
        String,
        nullable=False
    )

    status = Column(
        Enum(DocumentStatus),
        nullable=False
    )

    comment = Column(
        String,
        nullable=True
    )

    application = relationship(
        "ApplicationModel",
        back_populates="documents"
    )