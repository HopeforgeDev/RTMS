from datetime import datetime

from sqlalchemy import Column, Date, Integer, String, Boolean, ForeignKey, DateTime, Float

from app.db.base_class import Base

from sqlalchemy.orm import relationship


class Patient(Base):
    __tablename__ = "patient"
    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    gender = Column(Boolean, nullable=False)
    length = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    pathological_cases = Column(String)
    surgeries = Column(String)
    medicines = Column(String)
    permanent_health_symptoms = Column(String)
    contact_number = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)
    user_type = Column(String, default="patient")
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)

    appointments = relationship("Appointment", back_populates="patient")
