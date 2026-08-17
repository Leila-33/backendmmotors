from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from core.database.session import Base


class ApplicationFinancingModel(Base):

    __tablename__ = "application_financing"

    application_id = Column(
        String,
        ForeignKey("applications.id"),
        primary_key=True
    )

    down_payment = Column(Float, default=0)

    duration_months = Column(Integer)

    financed_amount = Column(Float)

    monthly_payment = Column(Float)

    # relation inverse
    application = relationship(
        "ApplicationModel",
        back_populates="financing"
    )