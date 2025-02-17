from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime

from app.db.base_class import Base


class Admin(Base):
    __tablename__ = "admin"
    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    middle_name =  Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    gender = Column(Boolean, nullable=False)
    contact_number = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String, nullable=False)
    user_type = Column(String, default="admin")
    secret_for_administration = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
