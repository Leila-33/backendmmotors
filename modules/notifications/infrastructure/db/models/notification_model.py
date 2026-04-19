from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.db.session import Base


class NotificationModel(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True)

    user_id = Column(String, ForeignKey("users.id"))
    application_id = Column(String, ForeignKey("applications.id"))

    title = Column(String)
    message = Column(String)

    type = Column(String)

    status = Column(String)
    is_read = Column(Boolean, default=False)

    created_at = Column(DateTime)

    # =====================
    # RELATIONS
    # =====================
    user = relationship("UserModel")
    application = relationship("ApplicationModel")