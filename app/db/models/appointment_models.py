from sqlalchemy import Column, Date, Integer, String, ForeignKey, DateTime, Time

from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Appointment(Base):
    __tablename__ = "appointment"
    id = Column(Integer, primary_key=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patient.id", ondelete="CASCADE"), nullable=False)
    office_id = Column(Integer, ForeignKey("office.id", ondelete="CASCADE"), nullable=False)
    probable_start_time = Column(Time, nullable=False)
    actual_end_time = Column(Time, nullable=False)
    appointment_status_id = Column(Integer, ForeignKey("appointment_status.id", ondelete="CASCADE"), nullable=False)
    appointment_taken_date = Column(Date, nullable=False)

    patient = relationship("Patient", back_populates="appointments")
    appointment_status = relationship("AppointmentStatus", back_populates="appointments")
    office = relationship("Office", back_populates="appointments")


class AppointmentStatus(Base):
    __tablename__ = "appointment_status"
    id = Column(Integer, primary_key=True, nullable=False)
    status = Column(String(10), nullable=False)

    appointments = relationship("Appointment", back_populates="appointment_status")