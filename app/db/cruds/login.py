from app.db.models.doctor_models import Doctor
from app.db.models.admin_models import Admin
from app.db.models.patient_models import Patient
from sqlalchemy.orm import Session


def get_user(username: str, db: Session):
    admin = db.query(Admin).filter(Admin.email == username).first()
    if admin:
        return admin
    doctor = db.query(Doctor).filter(Doctor.email == username).first()
    if doctor:
        return doctor
    patient = db.query(Patient).filter(Patient.email == username).first()
    if patient:
        return patient
