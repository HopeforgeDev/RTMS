from pydantic import BaseModel, EmailStr
from datetime import date, datetime, time
from typing import Optional

from fastapi import  Form
from pydantic import BaseModel



class UserOut(BaseModel):
    id: int
    email: EmailStr = "user@(patients-doctors-pharmacies).rtms.com"
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None
    type: str


class AppointmentBase(BaseModel):
    probable_start_time: time
    actual_end_time: time
    appointment_taken_date: date


class AppointmentCreate(AppointmentBase):
    pass


class Appointment(AppointmentBase):
    id: int
    patient_id: int
    office_id: int
    appointment_status_id: int

    class Config:
        orm_mode = True


class AppointmentStatusBase(BaseModel):
    status: str


class AppointmentStatusCreate(AppointmentStatusBase):
    pass


class AppointmentStatus(AppointmentStatusBase):
    id: int
    appointments: list[Appointment] = []

    class Config:
        orm_mode = True


class OfficeDateBase(BaseModel):
    pass


class OfficeDateCreate(OfficeDateBase):
    office_id: int
    office_doctor_availability_id: int


class OfficeDate(OfficeDateBase):
    id: int

    class Config:
        orm_mode = True


class OfficeDoctorAvailabilityBase(BaseModel):
    date: date
    start_time: time
    end_time: time
    is_available: bool
    reason_of_unavailability: Optional[str] = None


class OfficeDoctorAvailabilityCreate(OfficeDoctorAvailabilityBase):
    office_id: int


class OfficeDoctorAvailability(OfficeDoctorAvailabilityBase):
    id: int
    office_dates: list[OfficeDate] = []

    class Config:
        orm_mode = True


class InNetworkInsuranceBase(BaseModel):
    insurance_name: str


class InNetworkInsuranceCreate(InNetworkInsuranceBase):
    office_id: int


class InNetworkInsurance(InNetworkInsuranceBase):
    id: int

    class Config:
        orm_mode = True


class SpecializationChoose(BaseModel):
    specialization_name: str


class DoctorSpecializationBase(BaseModel):
    pass


class DoctorSpecializationCreate(DoctorSpecializationBase):
    doctor_id: int
    specialization_id: int


class DoctorSpecialization(DoctorSpecializationBase):
    id: int

    class Config:
        orm_mode = True


class SpecializationBase(BaseModel):
    specialization_name: str


class SpecializationCreate(SpecializationBase):
    pass


class Specialization(SpecializationBase):
    id: int
    doctor_specializations: list[DoctorSpecialization] = []

    class Config:
        orm_mode = True


class OfficeBase(BaseModel):
    time_slot_per_client_in_min: int
    first_consultation_fee: int
    followup_consultation_fee: int
    city: str
    country: str


class OfficeCreate(OfficeBase):
    doctor_id: int
    hospital_affiliation_id: int


class Office(OfficeBase):
    id: int
    appointments: list[Appointment] = []
    office_doctor_availabilities: list[OfficeDoctorAvailability] = []
    in_network_insurances: list[InNetworkInsurance] = []
    office_dates: list[OfficeDate] = []

    class Config:
        orm_mode = True


class HospitalAffiliationBase(BaseModel):
    hospital_name: str
    city: str
    country: str
    start_date: date
    end_date: date


class HospitalAffiliationCreate(HospitalAffiliationBase):
    doctor_id: int


class HospitalAffiliation(HospitalAffiliationBase):
    id: int
    offices: list[Office] = []

    class Config:
        orm_mode = True


class QualificationBase(BaseModel):
    qualification_name: str
    institute_name: str
    procurement_year: int


class QualificationCreate(QualificationBase):
    doctor_id: int


class Qualification(QualificationBase):
    id: int

    class Config:
        orm_mode = True


class AdminBase(BaseModel):
    first_name: str
    middle_name: str
    last_name: str
    gender: bool
    contact_number: str
    email: EmailStr = "user@admins.rtms.com"


class AdminFile(AdminBase):
    pass


class AdminCreate(AdminFile):
    password: str
    secret_for_administration: str


class Admin(AdminBase):
    id: int
    type: str = "admin"

    class Config:
        orm_mode = True


class AdminLogin(BaseModel):
    username: str
    password: str


class PatientBase(BaseModel):
    first_name: str
    middle_name: str
    last_name: str
    gender: bool
    date_of_birth: date
    contact_number: str
    email: EmailStr = "user@patients.rtms.com"


class PatientFile(PatientBase):
    length: int
    weight: int
    pathological_cases: str
    surgeries: str
    medicines: str
    permanent_health_symptoms: str


class PatientCreate(PatientFile):
    password: str


class Patient(PatientBase):
    id: int
    disabled: bool
    type: str = "patient"
    appointments: list[Appointment] = []

    class Config:
        orm_mode = True


class DoctorBase(BaseModel):
    first_name: str
    middle_name: str
    last_name: str
    professional_statement: str
    practicing_from: date
    email: EmailStr = "user@doctors.rtms.com"


class DoctorCreate(DoctorBase):
    password: str
    secret_for_doctor: str


class Doctor(DoctorBase):
    id: int
    disabled: bool
    type: str = "doctor"
    doctor_specializations: list[DoctorSpecialization] = []
    offices: list[Office] = []
    hospital_affiliations: list[HospitalAffiliation] = []
    qualifications: list[Qualification] = []

    class Config:
        orm_mode = True
