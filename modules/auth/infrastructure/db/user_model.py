from sqlalchemy import Column, String, Boolean, Enum, DateTime, func
from infrastructure.db.session import Base
from sqlalchemy.orm import relationship


from modules.core.enums import UserRole


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    role = Column(Enum(UserRole), default=UserRole.CLIENT, nullable=False)

    is_verified = Column(Boolean, default=False, nullable=False)

    accepted_cgu = Column(Boolean, default=False, nullable=False)

    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False, nullable=False)

    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    deleted_at = Column(DateTime, nullable=True)

    # =====================
    # RELATIONS
    # =====================

    events = relationship(
        "EventModel",
        back_populates="user"
    )

    applications = relationship(
        "ApplicationModel",
        back_populates="user"
    )

    notifications = relationship(
        "NotificationModel",
        back_populates="user"
    )
    
    test_drives = relationship(
    "TestDriveModel",
    back_populates="user",
    cascade="all, delete-orphan"
)
    favorites = relationship(
        "FavoriteModel",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    payments = relationship(
    "PaymentModel",
    back_populates="user",
    cascade="all, delete-orphan"
)
    
    messages = relationship(
            "TicketMessageModel",
            back_populates="sender"
        )
    
    tickets = relationship(
    "SupportTicketModel",
    foreign_keys="[SupportTicketModel.user_id]",
    back_populates="user"
)
    
    assigned_tickets = relationship(
    "SupportTicketModel",
    foreign_keys="[SupportTicketModel.assigned_to]"
)
    
    ticket_read_states = relationship(
    "TicketReadStateModel",
    back_populates="user",
    cascade="all, delete-orphan",
)