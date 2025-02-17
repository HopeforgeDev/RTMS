from operator import or_
from typing import Optional
from sqlalchemy.orm import Session

from sqlalchemy import update

from fastapi import Depends, HTTPException

from datetime import datetime, time, date

from app.db.session import get_db

from app.schemas import schemas

from app.db.models import appointment_models, doctor_models, office_models


def admit_patient_appointment_status(patient_appointment_status: schemas.AppointmentStatusCreate,
                                     db: Session = Depends(get_db)):
    new_patient_appointment_status = appointment_models.AppointmentStatus(**patient_appointment_status.dict())

    db.add(new_patient_appointment_status)
    db.commit()
    db.refresh(new_patient_appointment_status)

    return new_patient_appointment_status
#
#
# def create_app_booking_channel(app_booking_channel: schemas.AppBookingChannelCreate,
#                                db: Session = Depends(get_db)):
#     new_app_booking_channel = appointment_models.AppBookingChannel(**app_booking_channel.dict())
#
#     db.add(new_app_booking_channel)
#     db.commit()
#     db.refresh(new_app_booking_channel)
#
#     return new_app_booking_channel


def get_appointment_list_by_patient_id(
        patient_id: int,
        db: Session):
    appointments = db.query(
        appointment_models.Appointment).filter(
        appointment_models.Appointment.patient_id == patient_id).all()
    appointment_list = []
    for appointment in appointments:
        appointment_list.append(appointment)
    return appointment_list


def get_doctor_list_by_specialization_name_filter(
    db: Session, 
    specialization_name: str,
    name_filter: Optional[str] = None
):
    # Base query with proper joins
    query = db.query(schemas.Doctor).join(
        schemas.Doctor.specializations
    ).join(
        schemas.DoctorSpecialization.specialization
    ).filter(
        schemas.Specialization.name == specialization_name
    )
    
    # Add name filter if provided
    if name_filter:
        search_term = f"%{name_filter}%"
        query = query.filter(
            or_(
                schemas.Doctor.first_name.ilike(search_term),
                schemas.Doctor.middle_name.ilike(search_term),
                schemas.Doctor.last_name.ilike(search_term),
                (schemas.Doctor.first_name + " " + schemas.Doctor.last_name).ilike(search_term)
            )
        )
    
    return query.order_by(schemas.Doctor.last_name, schemas.Doctor.first_name).all()


def get_hospital_name_by_affiliation(db: Session, affiliation_id: int):
    return db.query(schemas.HospitalAffiliation.hospital_name).filter(
        schemas.HospitalAffiliation.id == affiliation_id
    ).scalar()


def get_office_with_hospital_info(db: Session, doctor_id: int):
    """Get offices with hospital names pre-attached"""
    return db.query(
        office_models.Office,
        doctor_models.HospitalAffiliation.hospital_name
    ).join(
        doctor_models.HospitalAffiliation,
        office_models.Office.hospital_affiliation_id == doctor_models.HospitalAffiliation.id
    ).filter(
        office_models.Office.doctor_id == doctor_id
    ).all()


def create_patient_appointment(appointment: schemas.AppointmentCreate,
                               patient_id: int,
                               appointment_status_id: int,
                               office_id: int,
                               db: Session):

    office_date_id = admitting_appointment_date(
        office_id=office_id,
        probable_start_time=appointment.probable_start_time,
        actual_end_time=appointment.actual_end_time,
        current_patient_id=patient_id,
        db=db)

    new_appointment = appointment_models.Appointment(**appointment.dict(),
                                                     patient_id=patient_id,
                                                     appointment_status_id=appointment_status_id,
                                                     office_id=office_id)
    update_office_time_availability(db=db,
                                    office_date_id=office_date_id,
                                    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return new_appointment


def update_office_time_availability(
        office_date_id: int,
        db: Session
):

    office_date = db.query(office_models.OfficeDate).filter(
        office_models.OfficeDate.id == office_date_id
    )

    if db.query(office_models.OfficeDate.time_availability).filter(
            office_models.OfficeDate.id == office_date_id
    ).first()[0]:
        office_date.update(
        {"time_availability": False},
        synchronize_session=False)
        db.commit()
    elif not db.query(office_models.OfficeDate.time_availability).filter(
            office_models.OfficeDate.id == office_date_id
    ).first()[0]:
        office_date.update(
        {"time_availability": True},
        synchronize_session=False)
        db.commit()


def delete_appointment_by_id(
        appointment_id: int,
        db: Session):
    existing_appointment = db.query(appointment_models.Appointment).filter(appointment_models.Appointment.id == appointment_id)
    if not existing_appointment.first():
        return 0

    office_id = db.query(
        appointment_models.Appointment.office_id).filter(
        appointment_models.Appointment.id == appointment_id
    ).first()[0]
    date = db.query(
        appointment_models.Appointment.appointment_taken_date).filter(
        appointment_models.Appointment.id == appointment_id
    ).first()[0]
    start_time = db.query(
        appointment_models.Appointment.probable_start_time).filter(
        appointment_models.Appointment.id == appointment_id
    ).first()[0]
    end_time = db.query(
        appointment_models.Appointment.actual_end_time).filter(
        appointment_models.Appointment.id == appointment_id
    ).first()[0]

    office_doctor_availability_id = db.query(
        office_models.OfficeDoctorAvailability.id
    ).filter(office_models.OfficeDoctorAvailability.date == date).first()[0]

    office_date_id = db.query(
        office_models.OfficeDate.id).filter(
        office_models.OfficeDate.start_time == start_time,
        office_models.OfficeDate.end_time == end_time,
        office_models.OfficeDate.office_id == office_id,
        office_models.OfficeDate.office_doctor_availability_id == office_doctor_availability_id,
    ).first()[0]
    update_office_time_availability(db=db,
                                    office_date_id=office_date_id)

    existing_appointment.delete(synchronize_session=False)
    db.commit()
    return 1


def get_all_appointments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(appointment_models.Appointment).offset(skip).limit(limit).all()


def get_all_appointments_for_office_id(db: Session, office_id: int, skip: int = 0, limit: int = 100):
    return db.query(appointment_models.Appointment).filter(
        appointment_models.Appointment.office_id == office_id).offset(skip).limit(limit).all()


def return_offices_for_appointment(start_time: datetime,
                                   end_time: datetime,
                                   db: Session = Depends(get_db),
                                   skip=0,
                                   limit=100):
    offices = db.query(office_models.Office.id).filter(
        office_models.OfficeDoctorAvailability.start_time < start_time
        and office_models.OfficeDoctorAvailability.end_time > end_time).offset(skip).limit(limit).all()

    if not offices:
        raise HTTPException(status_code=400,
                            detail="This time range is not available for all offices! "
                                   "Please, choose another time range.")

    return offices


def admitting_appointment_date(
        office_id: int,
        current_patient_id: int,
        probable_start_time: time,
        actual_end_time: time,
        db: Session = Depends(get_db)):
    try:
        office_date_id = db.query(
            office_models.OfficeDate.id).filter(
            office_models.OfficeDate.office_id == office_id,
            office_models.OfficeDate.start_time == probable_start_time,
            office_models.OfficeDate.end_time == actual_end_time).first()[0]
    except TypeError:
        return "This time range is out of boundaries for doctor's time and date! \nPlease, choose another time range."

    time_availability = db.query(
        office_models.OfficeDate.time_availability).filter(
        office_models.OfficeDate.id == office_date_id,
        office_models.OfficeDate.office_id == office_id
    ).first()[0]

    appointment_status_id = db.query(
        appointment_models.Appointment.appointment_status_id).filter(
        appointment_models.Appointment.office_id == office_id,
        appointment_models.Appointment.patient_id == current_patient_id
    ).first()

    print(appointment_status_id)
    if appointment_status_id:
        if time_availability is False and appointment_status_id[0] == 1:
            return "This time range is taken by another patient! \nPlease, choose another time range."

    return office_date_id

