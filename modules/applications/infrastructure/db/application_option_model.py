from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from core.database.session import Base

class ApplicationOptionModel(Base):
    __tablename__ = "application_options"

    id = Column(String, primary_key=True)

    application_id = Column(
        String,
        ForeignKey("applications.id"),
        nullable=False,
        index=True
    )

    option_id = Column(
        String,
        ForeignKey("options.id"),
        nullable=False,
        index=True
    )

    # =========================
    # RELATIONS
    # =========================

    application = relationship(
        "ApplicationModel",
        back_populates="options"
    )

    option = relationship(
        "OptionModel",
    back_populates="application_links"
    )