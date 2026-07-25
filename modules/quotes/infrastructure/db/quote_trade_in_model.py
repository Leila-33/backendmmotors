from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from core.database.session import Base


class QuoteTradeInModel(Base):

    __tablename__ = "quote_trade_in"

    quote_id = Column(
        String,
        ForeignKey("quotes.id", ondelete="CASCADE"),
        primary_key=True,
    )

    brand = Column(String, nullable=False)

    model = Column(String, nullable=False)

    year = Column(Integer, nullable=False)

    mileage = Column(Integer, nullable=False)

    condition = Column(String, nullable=False)

    estimated_value = Column(
        Float,
        nullable=False,
        default=0,
    )

    quote = relationship(
        "QuoteModel",
        back_populates="trade_in",
    )