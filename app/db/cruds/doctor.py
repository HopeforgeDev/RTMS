from datetime import date
from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException, status

from app.db.session import get_db

from app.schemas import schemas

from app.db.cruds import auth

from app.db.models import appointment_models, doctor_models, office_models

from app.core.hashing import Hasher
from app.schemas.schemas import SpecializationCreate, DoctorSpecializationCreate, QualificationCreate, \
    HospitalAffiliationCreate


def get_doctor(db: Session, doctor_id: int):
    return db.query(doctor_models.Doctor).filter(doctor_models.Doctor.id == doctor_id).first()


def get_doctor_by_email(db: Session, email: str):
    return db.query(doctor_models.Doctor).filter(doctor_models.Doctor.email == email).first()


def get_doctors(db: Session):
    return db.query(doctor_models.Doctor).all()


def get_doctor_list(db: Session):
    doctors = get_doctors(db=db)
    doctor_list = []
    for doctor in doctors:
        doctor_list.append(doctor)
    return doctor_list

def get_patient_id_list_by_office_id(office_id: int, db: Session):
    doctors = get_doctors(db=db)
    doctor_list = []
    for doctor in doctors:
        doctor_list.append(doctor)
    return doctor_list


def create_specialization(specialization: schemas.SpecializationCreate,
                          db: Session = Depends(get_db)):
    new_specialization = doctor_models.Specialization(**specialization.dict())

    db.add(new_specialization)
    db.commit()
    db.refresh(new_specialization)
    return new_specialization


def get_specializations(db: Session):
    return db.query(doctor_models.Specialization).all()


def get_specialization_name_list(db: Session):
    specialization_name_list: list[str] = []
    specialization_names = db.query(doctor_models.Specialization.specialization_name).all()
    for specialization_name in specialization_names:
        specialization_name_list.append(specialization_name[0])
    return specialization_name_list


def verify_uniqueness_for_doctor_with_specialization_by_ids(db: Session,
                                                            specialization_id: int,
                                                            doctor_id: int):
    return db.query(doctor_models.DoctorSpecialization).filter(
        doctor_models.DoctorSpecialization.specialization_id == specialization_id,
        doctor_models.DoctorSpecialization.doctor_id == doctor_id).first()


def verify_uniqueness_for_specialization_name(db: Session, specialization_name: str):
    return db.query(doctor_models.Specialization).filter(
        doctor_models.Specialization.specialization_name == specialization_name).first()


def get_doctor_id_list_by_specialization_name(db: Session, specialization_name: str, skip: int = 0, limit: int = 100):
    specialization = db.query(doctor_models.Specialization).filter(
        doctor_models.Specialization.specialization_name == specialization_name).first()

    if not specialization:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="The specialization name declared is not found!"
                                   "Please! enter the specialization name precisely")

    specialization_id = db.query(doctor_models.Specialization.id).filter(
        doctor_models.Specialization.specialization_name == specialization_name).first()[0]

    doctor_ids = db.query(
        doctor_models.DoctorSpecialization.doctor_id).filter(
        doctor_models.DoctorSpecialization.specialization_id == specialization_id).offset(skip).limit(limit).all()
    doctor_id_list: list[int] = []
    for doctor_id in doctor_ids:
        doctor_id_list.append(doctor_id[0])

    if not doctor_id_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="There is no doctors found for this specialization!")
    return doctor_id_list



def get_doctor_list_by_specialization_name(db: Session, specialization_name: str):
    specialization = db.query(doctor_models.Specialization).filter(
        doctor_models.Specialization.specialization_name == specialization_name).first()
    if not specialization:
        return "The specialization name declared is not found! \nPlease! enter the specialization name precisely"

    specialization_id = db.query(doctor_models.Specialization.id).filter(
        doctor_models.Specialization.specialization_name == specialization_name).first()[0]
    print(specialization_id)
    doctor_ids = db.query(
        doctor_models.DoctorSpecialization.doctor_id).filter(
        doctor_models.DoctorSpecialization.specialization_id == specialization_id).all()

    if not doctor_ids:
        return  "There is no doctors found for this specialization!"

    doctor_list = []
    for doctor_id in doctor_ids:
        doctor = db.query(
            doctor_models.Doctor).filter(
            doctor_models.Doctor.id == doctor_id[0]).first()
        doctor_list.append(doctor)
    print(doctor_list)
    return doctor_list


def create_qualification(
    qualification: QualificationCreate,
    db: Session = Depends(get_db)):

    new_qualification = doctor_models.Qualification(
    **qualification.__dict__
    )

    db.add(new_qualification)
    db.commit()
    db.refresh(new_qualification)
    return new_qualification


def get_qualification(
    db: Session,
    doctor_id: str,
    qualification_name: str,
    institute_name: str,
    procurement_year: date,
):
    
    return db.query(
    doctor_models.Qualification).filter(
        doctor_models.Qualification.doctor_id == doctor_id,
        doctor_models.Qualification.qualification_name == qualification_name,
        doctor_models.Qualification.institute_name == institute_name,
        doctor_models.Qualification.procurement_year == procurement_year
        ).first()
        

def get_qualification_id_by_qualification_name(
    db: Session,
    doctor_id: str,
    qualification_name_list: list[str]
):

    qualification_name_id_list: list[int] = []

    for qualification_name in qualification_name_list:

        qualification_name_ids = db.query(
        doctor_models.Qualification.id).filter(
            doctor_models.Qualification.doctor_id == doctor_id,
            doctor_models.Qualification.qualification_name == qualification_name
            ).all()
        if qualification_name_ids:

            for qualification_name_id in qualification_name_ids:
                qualification_name_id_list.append(qualification_name_id[0])
    return qualification_name_id_list


def get_qualification_id_by_institute_name(
    db: Session,
    doctor_id: str,
    institute_name_list: list[str]
):

    institute_name_id_list: list[int] = []

    for institute_name in institute_name_list:

        institute_name_ids = db.query(
        doctor_models.Qualification.id).filter(
            doctor_models.Qualification.doctor_id == doctor_id,
            doctor_models.Qualification.institute_name == institute_name
            ).all()
        if institute_name_ids:

            for institute_name_id in institute_name_ids:
                institute_name_id_list.append(institute_name_id[0])
    return institute_name_id_list


def get_qualification_list_by_doctor_id(
    db: Session,
    doctor_id: int,
):
    qualification_list = []
    qualifications = db.query(
        doctor_models.Qualification).filter(doctor_models.Qualification.doctor_id == doctor_id).all()
    for qualification in qualifications:
        qualification_list.append(qualification)
        print(qualification)
    return qualification_list


def get_doctor_qualification_by_doctor_id(
    db: Session,
    doctor_id: str
):
    
    return db.query(doctor_models.Qualification).filter(
        doctor_models.Qualification.doctor_id == doctor_id
            ).first()


def valid_presence_qualification(db: Session):

    validated = False

    if db.query(doctor_models.Qualification).first():
        validated = True
    
    return validated


def get_doctor_qualifications(db: Session, doctor_id: str, skip: int = 0, limit: int = 100):
    return db.query(
        doctor_models.Qualification).filter(
        doctor_models.Qualification.doctor_id == doctor_id).offset(skip).limit(limit).all()


def create_hospital_affiliation(
        hospital_affiliation: HospitalAffiliationCreate,
        db: Session
        ):
    new_hospital_affiliation = doctor_models.HospitalAffiliation(
    **hospital_affiliation.__dict__
            )

    db.add(new_hospital_affiliation)
    db.commit()
    db.refresh(new_hospital_affiliation)
    return new_hospital_affiliation


def get_hospital_affiliation(
    db: Session,
    doctor_id: str,
    hospital_name: str,
    city: str,
    country: str,
    start_date: date,
    end_date: date):        

    return db.query(
    doctor_models.HospitalAffiliation).filter(
        doctor_models.HospitalAffiliation.doctor_id == doctor_id,
        doctor_models.HospitalAffiliation.hospital_name == hospital_name,
        doctor_models.HospitalAffiliation.city == city,
        doctor_models.HospitalAffiliation.country == country,
        doctor_models.HospitalAffiliation.start_date == start_date,
        doctor_models.HospitalAffiliation.end_date == end_date,        
        ).first()


def valid_presence_hospital_affiliation(db: Session):

    validated = False

    if db.query(doctor_models.HospitalAffiliation).first():
        validated = True
    
    return validated


def get_doctor_hospital_affiliation_list_by_doctor_id(
    db: Session,
    doctor_id: int,
):
    hospital_affiliation_list = []
    hospital_affiliations = db.query(
        doctor_models.HospitalAffiliation).filter(doctor_models.HospitalAffiliation.doctor_id == doctor_id).all()
    for hospital_affiliation in hospital_affiliations:
        hospital_affiliation_list.append(hospital_affiliation)
    return hospital_affiliation_list


# def get_doctor_hospital_affiliation_list_by_office_id(
#     db: Session,
#     office_id: int,
# ):
#     hospital_affiliation_list = []
#     doctor_id = db.query(
#         doctor_models.Office.doctor_id).filter(
#             office_models.Office.id == office_id
#             ).first()[0]
#     hospital_affiliations = db.query(
#         doctor_models.HospitalAffiliation).filter(
#             doctor_models.HospitalAffiliation.doctor_id == doctor_id
#             ).all()
#     for hospital_affiliation in hospital_affiliations:
#         hospital_affiliation_list.append(hospital_affiliation)
#     return hospital_affiliation_list


def get_doctor_hospital_affiliation_names_by_doctor_id(
    db: Session,
    doctor_id: str,
):
    hospital_affiliation_name_list: list[str] = []

    hospital_affiliation_names = db.query(
        doctor_models.HospitalAffiliation.hospital_name).filter(
            doctor_models.HospitalAffiliation.doctor_id == doctor_id
                ).all()
    if hospital_affiliation_names:

        for hospital_affiliation_name in hospital_affiliation_names:
            hospital_affiliation_name_list.append(hospital_affiliation_name[0])
    return hospital_affiliation_name_list


def get_doctor_hospital_affiliation_names_by_patient_id(
    db: Session,
    patient_id: str,
):
    hospital_affiliation_name_list: list[str] = []

    office_ids = db.query(
        appointment_models.Appointment.office_id).filter(
            appointment_models.Appointment.patient_id == patient_id
                ).all()
    if office_ids:
        for office_id in office_ids:
            doctor_id = db.query(
                office_models.Office.doctor_id).filter(
                    office_models.Office.id == office_id[0]
                        ).first()[0]
            hospital_affiliation_names = db.query(
                doctor_models.HospitalAffiliation.hospital_name).filter(
                    doctor_models.HospitalAffiliation.doctor_id == doctor_id
                        ).all()
            if hospital_affiliation_names:
                for hospital_affiliation_name in hospital_affiliation_names:
                    hospital_affiliation_name_list.append(hospital_affiliation_name[0])
    return hospital_affiliation_name_list


def get_doctor_hospital_affiliation_by_doctor_id(
    db: Session,
    doctor_id: str
):
    
    return db.query(
        doctor_models.HospitalAffiliation).filter(
        doctor_models.HospitalAffiliation.doctor_id == doctor_id
            ).first()


def get_doctor_hospital_affiliation_by_hospital_name(
    db: Session,
    hospital_name_list: list[str],
    doctor_id: str
):  

    hospital_id_list: list[int] = []

    for hospital_name in hospital_name_list:

        hospital_name_doctor_ids = db.query(
            doctor_models.HospitalAffiliation.id).filter(
            doctor_models.HospitalAffiliation.hospital_name == hospital_name,
            doctor_models.HospitalAffiliation.doctor_id == doctor_id
                ).all()
        if hospital_name_doctor_ids:

            for hospital_name_id in hospital_name_doctor_ids:
                hospital_id_list.append(hospital_name_id[0])
    return hospital_id_list


def get_doctor_hospital_affiliation_by_city(
    db: Session,
    city_list: list[str],
    doctor_id: str

):

    hospital_id_list: list[int] = []

    for city in city_list:

        city_doctor_ids = db.query(
        doctor_models.HospitalAffiliation.id).filter(
            doctor_models.HospitalAffiliation.city == city,
            doctor_models.HospitalAffiliation.doctor_id == doctor_id
            ).all()

        if city_doctor_ids:

            for hospital_name_id in city_doctor_ids:
                hospital_id_list.append(hospital_name_id[0])

    return hospital_id_list


def get_doctor_hospital_affiliation_by_start_date(
    db: Session,
    start_date_list: list[str],
    doctor_id: str
):
    
    hospital_id_list: list[int] = []

    for start_date in start_date_list:

        start_date_doctor_ids = db.query(
        doctor_models.HospitalAffiliation.id).filter(
            doctor_models.HospitalAffiliation.start_date == start_date,
            doctor_models.HospitalAffiliation.doctor_id == doctor_id
            ).all()

        if start_date_doctor_ids:

            for hospital_name_id in start_date_doctor_ids:
                hospital_id_list.append(hospital_name_id[0])

    return hospital_id_list


def get_doctor_hospital_affiliation_by_end_date(
    db: Session,
    end_date_list: list[str],
    doctor_id: str
):
    
    hospital_id_list: list[int] = []

    for end_date in end_date_list:

        end_date_doctor_ids = db.query(
        doctor_models.HospitalAffiliation.id).filter(
            doctor_models.HospitalAffiliation.end_date == end_date,
            doctor_models.HospitalAffiliation.doctor_id == doctor_id
            ).all()

        if end_date_doctor_ids:

            for hospital_name_id in end_date_doctor_ids:
                hospital_id_list.append(hospital_name_id[0])

    return hospital_id_list


def get_doctor_hospital_affiliations(db: Session, doctor_id: str, skip: int = 0, limit: int = 100):
    return db.query(doctor_models.HospitalAffiliation).filter(
        doctor_models.HospitalAffiliation.doctor_id == doctor_id).offset(skip).limit(limit).all()


def create_doctor_specialization(
                                 specialization: DoctorSpecializationCreate,
                                 db: Session = Depends(get_db)):
    new_doctor_specialization = doctor_models.DoctorSpecialization(
        **specialization.__dict__
)

    db.add(new_doctor_specialization)
    db.commit()
    db.refresh(new_doctor_specialization)
    return new_doctor_specialization


def update_specialization_by_id(specialization_id: int, specialization: schemas.SpecializationCreate, db: Session):
    existing_specialization = db.query(doctor_models.Specialization).filter(doctor_models.Specialization.id == specialization_id)
    if not existing_specialization.first():
        return 0
    specialization.__dict__.update(
        id=specialization_id
    )  # update dictionary with new key value of owner_id
    existing_specialization.update(specialization.__dict__)
    db.commit()
    return 1


def delete_specialization_by_id(specialization_id: int, db: Session):
    existing_specialization = db.query(doctor_models.Specialization).filter(doctor_models.Specialization.id == specialization_id)
    if not existing_specialization.first():
        return 0
    existing_specialization.delete(synchronize_session=False)
    db.commit()
    return 1


def get_specialization_name_by_doctor_id(
    db: Session,
    doctor_id: int
):
    print(doctor_id)
    specialization_id = db.query(
    doctor_models.DoctorSpecialization.specialization_id).filter(
        doctor_models.DoctorSpecialization.doctor_id == doctor_id
    ).first()[0]

    return db.query(
    doctor_models.Specialization.specialization_name).filter(
        doctor_models.Specialization.id == specialization_id
    ).first()[0]


def get_specialization_id_by_specialization_name(
    db: Session,
    specialization_name: str
):

    return db.query(
    doctor_models.Specialization.id).filter(
        doctor_models.Specialization.specialization_name == specialization_name
    ).first()[0]


def valid_presence_specialization(db: Session):
    validated = False
    if db.query(doctor_models.Specialization.id).first():
        validated = True
    return validated


def get_specific_doctor_specialization(
    db: Session,
    doctor_id: int):

    return db.query(
        doctor_models.DoctorSpecialization).filter(
        doctor_models.DoctorSpecialization.doctor_id == doctor_id
            ).first()
        

def valid_presence_doctor_specialization(db: Session, skip: int = 0, limit: int = 100):

    validated = False

    if db.query(doctor_models.DoctorSpecialization).first():
        validated = True
    
    return validated


def deactivate_doctor_by_id(doctor_id: int, db: Session):
    existing_doctor = db.query(doctor_models.Doctor).filter(doctor_models.Doctor.id == doctor_id)
    if not existing_doctor.first():
        return 0
    disability = db.query(doctor_models.Doctor.disabled).filter(doctor_models.Doctor.id == doctor_id)
    if not disability.first()[0]:
        existing_doctor.update({'disabled': True})
        db.commit()
        return 1
    return 0


def activate_doctor_by_id(doctor_id: int, db: Session):
    existing_doctor = db.query(doctor_models.Doctor).filter(doctor_models.Doctor.id == doctor_id)
    if not existing_doctor.first():
        return 0
    disability = db.query(doctor_models.Doctor.disabled).filter(doctor_models.Doctor.id == doctor_id)
    if disability.first()[0]:
        existing_doctor.update({'disabled': False})
        db.commit()
        return 1
    return 0


def update_doctor_by_id(doctor_id: int, doctor: schemas.DoctorCreate, db: Session):
    existing_doctor = db.query(doctor_models.Doctor).filter(doctor_models.Doctor.id == doctor_id)
    if not existing_doctor.first():
        return 0
    doctor.__dict__.update(
        id=doctor_id
    )  # update dictionary with new key value of owner_id
    existing_doctor.update(doctor.__dict__)
    db.commit()
    return 1


def delete_doctor_by_id(doctor_id: int, db: Session):
    existing_doctor = db.query(doctor_models.Doctor).filter(doctor_models.Doctor.id == doctor_id)
    if not existing_doctor.first():
        return 0
    existing_doctor.delete(synchronize_session=False)
    db.commit()
    return 1


def create_doctor(
        doctor: schemas.DoctorCreate,
        db: Session = Depends(get_db)):

    new_doctor = doctor_models.Doctor(
        first_name=doctor.first_name,
        middle_name=doctor.middle_name,
        last_name=doctor.last_name,
        professional_statement=doctor.professional_statement,
        practicing_from=doctor.practicing_from,
        email=doctor.email,
        password=doctor.password,
        secret_for_doctor=doctor.secret_for_doctor)

    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return new_doctor


def search_for_doctor_name_by_doctor_id(
        db: Session,
        searched_doctor_id: int
):

    searched_doctor_f_name = db.query(
        doctor_models.Doctor.first_name).filter(
        doctor_models.Doctor.id == searched_doctor_id
    ).first()[0]

    searched_doctor_m_name = db.query(
        doctor_models.Doctor.middle_name).filter(
        doctor_models.Doctor.id == searched_doctor_id
    ).first()[0]

    searched_doctor_l_name = db.query(
        doctor_models.Doctor.last_name).filter(
        doctor_models.Doctor.id == searched_doctor_id
    ).first()[0]

    return searched_doctor_f_name + " " + searched_doctor_m_name + " " + searched_doctor_l_name


def search_for_doctor_id_by_doctor_full_name(
        db: Session,
        searched_doctor_full_name: str
):

    searched_doctor_full_name_list = searched_doctor_full_name.split(" ")

    searched_doctor_full_name_list = [
        searched_doctor_full_name.lower().capitalize() for searched_doctor_full_name in searched_doctor_full_name_list]

    searched_doctor_first_name_ids = db.query(
        doctor_models.Doctor.id).filter(
        doctor_models.Doctor.first_name == searched_doctor_full_name_list[0]
    ).all()

    searched_doctor_first_name_id_list = [
        searched_doctor_first_name_id[0] for searched_doctor_first_name_id in searched_doctor_first_name_ids
    ]

    if not searched_doctor_first_name_id_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'No result'
        )

    elif len(searched_doctor_full_name_list) == 1:
        return searched_doctor_first_name_id_list

    elif len(searched_doctor_full_name_list) == 2:
        searched_doctor_last_name_ids = db.query(
            doctor_models.Doctor.id).filter(
            doctor_models.Doctor.last_name == searched_doctor_full_name_list[1]
        ).all()

        searched_doctor_last_name_id_list = [
            searched_doctor_last_name_id[0] for searched_doctor_last_name_id in searched_doctor_last_name_ids
        ]

        if not searched_doctor_last_name_id_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'No result'
            )

        searched_doctor_first_last_name_id_list = [
            searched_doctor_last_name_id for searched_doctor_last_name_id, searched_doctor_first_name_id in zip(searched_doctor_last_name_id_list, searched_doctor_first_name_id_list) if searched_doctor_last_name_id == searched_doctor_first_name_id
        ]

        return searched_doctor_first_last_name_id_list

    elif len(searched_doctor_full_name_list) == 3:
        searched_doctor_middle_name_ids = db.query(
            doctor_models.Doctor.id).filter(
            doctor_models.Doctor.middle_name == searched_doctor_full_name_list[1]
        ).all()

        searched_doctor_middle_name_id_list = [
            searched_doctor_middle_name_id[0] for searched_doctor_middle_name_id in searched_doctor_middle_name_ids
        ]

        if not searched_doctor_middle_name_id_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'No result'
            )
        searched_doctor_last_name_ids = db.query(
            doctor_models.Doctor.id).filter(
            doctor_models.Doctor.last_name == searched_doctor_full_name_list[2]
        ).all()

        searched_doctor_last_name_id_list = [
            searched_doctor_last_name_id[0] for searched_doctor_last_name_id in searched_doctor_last_name_ids
        ]

        if not searched_doctor_last_name_id_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'No result'
            )

        searched_doctor_full_name_id_list = [
            searched_doctor_last_name_id for searched_doctor_last_name_id, searched_doctor_first_name_id, searched_doctor_middle_name_id in
            zip(searched_doctor_last_name_id_list, searched_doctor_first_name_id_list, searched_doctor_middle_name_id_list) if
            searched_doctor_last_name_id == searched_doctor_first_name_id == searched_doctor_middle_name_id
        ]

        return searched_doctor_full_name_id_list

    elif len(searched_doctor_full_name_list) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Please! enter doctor\'s full name'
        )

