from sqlalchemy import Column, String, Boolean
from infrastructure.db.session import Base
class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    accepted_cgu = Column(Boolean)