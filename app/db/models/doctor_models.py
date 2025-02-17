from sqlalchemy import Column, Date, Integer, String, ForeignKey, DateTime, Boolean, Float

from datetime import datetime

from app.db.base_class import Base

from sqlalchemy.orm import relationship


class Specialization(Base):
    __tablename__ = "specialization"
    id = Column(Integer, primary_key=True, nullable=False)
    specialization_name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)

    doctor_specializations = relationship("DoctorSpecialization", back_populates="specialization")


class DoctorSpecialization(Base):
    __tablename__ = "doctor_specialization"
    id = Column(Integer, primary_key=True, nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctor.id", ondelete="Cascade"), nullable=False)
    specialization_id = Column(Integer, ForeignKey("specialization.id", ondelete="Cascade"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(),)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)

    doctor = relationship("Doctor", back_populates="doctor_specializations")
    specialization = relationship("Specialization", back_populates="doctor_specializations")


class Qualification(Base):
    __tablename__ = "qualification"
    id = Column(Integer, primary_key=True, nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctor.id", ondelete="Cascade"), nullable=False)
    qualification_name = Column(String, nullable=False)
    institute_name = Column(String)
    procurement_year = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)

    doctor = relationship("Doctor", back_populates="qualifications")


class Doctor(Base):
    __tablename__ = "doctor"
    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    professional_statement = Column(String(4000), nullable=False)
    practicing_from = Column(Date, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String, nullable=False)
    secret_for_doctor = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)
    user_type = Column(String, default="doctor")
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)

    offices = relationship("Office", back_populates="doctor")
    hospital_affiliations = relationship("HospitalAffiliation", back_populates="doctor")
    qualifications = relationship("Qualification", back_populates="doctor")
    doctor_specializations = relationship("DoctorSpecialization", back_populates="doctor")


class HospitalAffiliation(Base):
    __tablename__ = "hospital_affiliation"
    id = Column(Integer, primary_key=True, nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctor.id", ondelete="Cascade"), nullable=False)
    hospital_name = Column(String(100), nullable=False)
    city = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    offices = relationship("Office", back_populates="hospital_affiliation")
    doctor = relationship("Doctor", back_populates="hospital_affiliations")
