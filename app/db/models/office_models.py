from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, Date, Time

from sqlalchemy.orm import relationship

from app.db.base_class import Base

from datetime import datetime


class Office(Base):
    __tablename__ = "office"
    id = Column(Integer, primary_key=True, nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctor.id", ondelete="CASCADE"))
    hospital_affiliation_id = Column(Integer, ForeignKey("hospital_affiliation.id", ondelete="CASCADE"), nullable=False)
    time_slot_per_client_in_min = Column(Integer, nullable=False)
    first_consultation_fee = Column(Integer, nullable=False)
    followup_consultation_fee = Column(Integer, nullable=False)
    city = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)

    appointments = relationship("Appointment", back_populates="office")
    doctor = relationship("Doctor", back_populates="offices")
    hospital_affiliation = relationship("HospitalAffiliation", back_populates="offices")
    office_doctor_availabilities = relationship("OfficeDoctorAvailability", back_populates="office")
    in_network_insurances = relationship("InNetworkInsurance", back_populates="office")
    office_dates = relationship("OfficeDate", back_populates="office")


class OfficeDoctorAvailability(Base):
    __tablename__ = "office_doctor_availability"
    id = Column(Integer, primary_key=True, nullable=False)
    office_id = Column(Integer, ForeignKey("office.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False, default=Time)
    end_time = Column(Time, nullable=False, default=Time)
    is_available = Column(Boolean, nullable=False)
    reason_of_unavailability = Column(String(500))

    office = relationship("Office", back_populates="office_doctor_availabilities")
    office_dates = relationship("OfficeDate", back_populates="office_doctor_availability")


class InNetworkInsurance(Base):
    __tablename__ = "in_network_insurance"
    id = Column(Integer, primary_key=True, nullable=False)
    insurance_name = Column(String(200), nullable=False)
    office_id = Column(Integer, ForeignKey("office.id", ondelete="CASCADE"), nullable=False)

    office = relationship("Office", back_populates="in_network_insurances")


class OfficeDate(Base):
    __tablename__ = "office_date"
    id = Column(Integer, primary_key=True, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    time_availability = Column(Boolean, default=True, nullable=False)
    office_id = Column(Integer, ForeignKey("office.id", ondelete="CASCADE"), nullable=False)
    office_doctor_availability_id = Column(Integer, ForeignKey("office_doctor_availability.id",
                                                               ondelete="CASCADE"), nullable=False)

    office = relationship("Office", back_populates="office_dates")
    office_doctor_availability = relationship("OfficeDoctorAvailability", back_populates="office_dates")
