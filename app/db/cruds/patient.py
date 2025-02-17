from sqlalchemy.orm import Session

from fastapi import Depends

from app.db.session import get_db

from app.db.models import patient_models

from app.schemas.schemas import PatientCreate


def get_patient(db: Session, patient_id: int):
    return db.query(patient_models.Patient).filter(patient_models.Patient.id == patient_id).first()


def get_patient_by_email(db: Session, email: str):
    return db.query(patient_models.Patient).filter(patient_models.Patient.email == email).first()


def get_patients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(patient_models.Patient).offset(skip).limit(limit).all()

def get_patient_list(db: Session):
    patients = get_patients(db=db)
    patient_list = []
    for patient in patients:
        patient_list.append(patient)
    return patient_list


def deactivate_patient_by_id(patient_id: int, db: Session):
    existing_patient = db.query(patient_models.Patient).filter(patient_models.Patient.id == patient_id)
    if not existing_patient.first():
        return 0
    disability = db.query(patient_models.Patient.disabled).filter(patient_models.Patient.id == patient_id)
    if not disability.first()[0]:
        existing_patient.update({'disabled': True})
        db.commit()
        return 1
    return 0


def activate_patient_by_id(patient_id: int, db: Session):
    existing_patient = db.query(patient_models.Patient).filter(patient_models.Patient.id == patient_id)
    if not existing_patient.first():
        return 0
    disability = db.query(patient_models.Patient.disabled).filter(patient_models.Patient.id == patient_id)
    if disability.first()[0]:
        existing_patient.update({'disabled': False})
        db.commit()
        return 1
    return 0


def update_patient_by_id(patient_id: int, patient: PatientCreate, db: Session):
    existing_patient = db.query(patient_models.Patient).filter(patient_models.Patient.id == patient_id)
    if not existing_patient.first():
        return 0
    patient.__dict__.update(
        id=patient_id
    )  # update dictionary with new key value of owner_id
    existing_patient.update(patient.__dict__)
    db.commit()
    return existing_patient


def delete_patient_by_id(patient_id: int, db: Session):
    existing_patient = db.query(patient_models.Patient).filter(patient_models.Patient.id == patient_id)
    if not existing_patient.first():
        return 0
    existing_patient.delete(synchronize_session=False)
    db.commit()
    return 1


def create_patient(
        patient: PatientCreate,
        db: Session = Depends(get_db)):

    new_patient = patient_models.Patient(
        first_name=patient.first_name,
        middle_name=patient.middle_name,
        last_name=patient.last_name,
        gender=patient.gender,
        contact_number=patient.contact_number,
        email=patient.email,
        password=patient.password,
        length=patient.length,
        weight=patient.weight,
        date_of_birth=patient.date_of_birth,
        pathological_cases=patient.pathological_cases,
        surgeries=patient.surgeries,
        medicines=patient.medicines,
        permanent_health_symptoms=patient.permanent_health_symptoms)

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient
