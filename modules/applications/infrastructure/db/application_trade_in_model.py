from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from infrastructure.db.session import Base


class ApplicationTradeInModel(Base):

    __tablename__ = "application_trade_in"

    application_id = Column(
        String,
        ForeignKey("applications.id"),
        primary_key=True
    )

    brand = Column(String)
    model = Column(String)
    year = Column(Integer)
    mileage = Column(Integer)

    condition = Column(String)

    estimated_value = Column(Float)

    # relation inverse
    application = relationship(
        "ApplicationModel",
        back_populates="trade_in"
    )