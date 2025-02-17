from sqlalchemy.orm import Session

from fastapi import Depends

from app.db.session import get_db

from app.schemas import schemas

from datetime import timedelta, datetime

from app.db.models import office_models, doctor_models


def create_office(office: schemas.OfficeCreate,
                  db: Session = Depends(get_db)):

    office = office_models.Office(**office.dict())

    db.add(office)

    db.commit()
    db.refresh(office)

    return office


def update_office_by_id(office_id: int, office: schemas.OfficeCreate, db: Session):
    existing_office = db.query(office_models.Office).filter(office_models.Office.id == office_id)
    if not existing_office.first():
        return 0
    office.__dict__.update(
        id=office_id
    )  # update dictionary with new key value of owner_id
    existing_office.update(office.__dict__)
    db.commit()
    return existing_office.first()


def update_doctor_availability_by_id(id: int, office_id: int, office_doctor_availability: schemas.OfficeDoctorAvailabilityCreate, db: Session):
    existing_office_doctor_availability = db.query(
        office_models.OfficeDoctorAvailability).filter(
        office_models.OfficeDoctorAvailability.office_id == office_id
        and office_models.OfficeDoctorAvailability.id == id)
    if not existing_office_doctor_availability.first():
        return None
    office_doctor_availability.__dict__.update(
        id=id,
        office_id=office_id
    )  # update dictionary with new key value of owner_id
    existing_office_doctor_availability.update(office_doctor_availability.__dict__)
    db.commit()
    return existing_office_doctor_availability.first()


def delete_office_by_id(office_id: int, db: Session):
    existing_office = db.query(office_models.Office).filter(office_models.Office.id == office_id)
    if not existing_office.first():
        return 0
    existing_office.delete(synchronize_session=False)
    db.commit()
    return 1


def delete_office_doctor_availability_by_id(office_doctor_availability_id: int, db: Session):
    existing_office = db.query(
        office_models.OfficeDoctorAvailability).filter(
            office_models.OfficeDoctorAvailability.id == office_doctor_availability_id)
    if not existing_office.first():
        return 0
    existing_office.delete(synchronize_session=False)
    db.commit()
    return 1


def know_office_doctor_availability(office_doctor_availability: schemas.OfficeDoctorAvailabilityCreate,
                                    office_id: int,
                                    db: Session = Depends(get_db)):

    office_doctor_availability = office_models.OfficeDoctorAvailability(**office_doctor_availability.dict(),
                                                                        office_id=office_id)

    db.add(office_doctor_availability)

    db.commit()
    db.refresh(office_doctor_availability)

    return office_doctor_availability


def update_in_network_insurance(insurance_id: int, office_id: int, in_network_insurance: schemas.InNetworkInsuranceCreate, db: Session):
    existing_insurance = db.query(
        office_models.InNetworkInsurance).filter(
            office_models.InNetworkInsurance.office_id == office_id
            and office_models.InNetworkInsurance.id == insurance_id)
    if not existing_insurance.first():
        return None
    in_network_insurance.__dict__.update(
        id=insurance_id,
        office_id=office_id
    )  # update dictionary with new key value of owner_id
    existing_insurance.update(in_network_insurance.__dict__)
    db.commit()
    return existing_insurance.first()


def delete_insurance_by_office_id(office_id: int, db: Session):
    existing_office = db.query(office_models.InNetworkInsurance).filter(office_models.InNetworkInsurance.office_id == office_id)
    if not existing_office.first():
        return 0
    existing_office.delete(synchronize_session=False)
    db.commit()
    return 1


def admit_in_network_insurance(in_network_insurance: schemas.InNetworkInsuranceCreate,
                               db: Session):
    in_network_insurance = office_models.InNetworkInsurance(**in_network_insurance.dict())

    db.add(in_network_insurance)
    db.commit()
    db.refresh(in_network_insurance)

    return in_network_insurance


def create_doctor_availability(
        office_doctor_availability = schemas.OfficeDoctorAvailabilityCreate,
        db: Session = Depends(get_db)):

    new_office_doctor_availability = office_models.OfficeDoctorAvailability(**office_doctor_availability.__dict__)
    db.add(new_office_doctor_availability)
    db.commit()
    db.refresh(new_office_doctor_availability)
    return new_office_doctor_availability


def create_office_geolocation(
        office_id: int,
        office_longitude: float,
        office_latitude: float,
        db: Session):

    new_office_geolocation = office_models.OfficeGeoLocation(
        office_id=office_id,
        office_longitude=office_longitude,
        office_latitude=office_latitude,

    )
    db.add(new_office_geolocation)
    db.commit()
    db.refresh(new_office_geolocation)
    return new_office_geolocation


def create_office_date(office_doctor_availability_id: int,
                       office_id: int,
                       db: Session):

    start_time = db.query(
        office_models.OfficeDoctorAvailability.start_time).filter(
        office_models.OfficeDoctorAvailability.id == office_doctor_availability_id).first()[0]

    end_time = db.query(
        office_models.OfficeDoctorAvailability.end_time).filter(
        office_models.OfficeDoctorAvailability.id == office_doctor_availability_id).first()[0]

    time_slot_per_clint_in_min = db.query(
        office_models.Office.time_slot_per_client_in_min).filter(
        office_models.Office.id == office_id
    ).first()[0]
    start_time = datetime.combine(datetime(1,1,1,0,0,0), start_time)
    end_time = datetime.combine(datetime(1,1,1,0,0,0), end_time)
    duration = end_time - start_time
    times = 1
    end_time = start_time + timedelta(minutes=int(time_slot_per_clint_in_min))
    office_date = office_models.OfficeDate(start_time=start_time,
                                           end_time=end_time,
                                           office_id=office_id,
                                           office_doctor_availability_id=office_doctor_availability_id)

    db.add(office_date)
    db.commit()
    db.refresh(office_date)

    while int(time_slot_per_clint_in_min) * times < int(duration.total_seconds() / 60):

        start_time = end_time
        end_time = end_time + timedelta(minutes=int(time_slot_per_clint_in_min))
        office_date = office_models.OfficeDate(end_time=end_time,
                                               start_time=start_time,
                                               office_id=office_id,
                                               office_doctor_availability_id=office_doctor_availability_id)
        db.add(office_date)
        db.commit()
        db.refresh(office_date)

        times = times + 1
    return "The office dates are created"


def delete_office_date_by_id(office_date_id: int, db: Session):
    existing_office_date = db.query(office_models.OfficeDate).filter(office_models.OfficeDate.id == office_date_id)
    if not existing_office_date.first():
        return 0
    existing_office_date.delete(synchronize_session=False)
    db.commit()
    return 1


def update_office_date_by_office_id(office_id: int,
                                         office_date: schemas.OfficeDateCreate,
                                         db: Session):
    start_time = db.query(
        office_models.OfficeDoctorAvailability.start_time).filter(
        office_models.OfficeDoctorAvailability.id == office_date.office_doctor_availability_id).first()[0]

    end_time = db.query(
        office_models.OfficeDoctorAvailability.end_time).filter(
        office_models.OfficeDoctorAvailability.id == office_date.office_doctor_availability_id).first()[0]

    time_slot_per_clint_in_min = db.query(
        office_models.Office.time_slot_per_client_in_min).filter(
        office_models.Office.id == office_id
    ).first()[0]
    start_time = datetime.combine(datetime(1,1,1,0,0,0), start_time)
    end_time = datetime.combine(datetime(1,1,1,0,0,0), end_time)
    duration = end_time - start_time
    times = 1
    end_time = start_time + timedelta(minutes=int(time_slot_per_clint_in_min))

    existing_office_date_id = db.query(office_models.OfficeDate.id).filter(
        office_models.OfficeDate.office_id == office_id
        )
    existing_office_date_id_list = []
    if existing_office_date_id.first():
        existing_office_date_ids = existing_office_date_id.all()
        for existing_office_date_id in existing_office_date_ids:
            existing_office_date_id_list.append(existing_office_date_id[0])
            delete_office_date_by_id(existing_office_date_id[0], db=db)

    office_date = office_models.OfficeDate(start_time=start_time,
                                           end_time=end_time,
                                           office_id=office_id,
                                           office_doctor_availability_id=office_date.office_doctor_availability_id)

    db.add(office_date)
    db.commit()
    db.refresh(office_date)

    while int(time_slot_per_clint_in_min) * times < int(duration.total_seconds() / 60):
        start_time = end_time
        end_time = end_time + timedelta(minutes=int(time_slot_per_clint_in_min))
        office_date = office_models.OfficeDate(end_time=end_time,
                                               start_time=start_time,
                                               office_id=office_id,
                                               office_doctor_availability_id=office_date.office_doctor_availability_id)
        db.add(office_date)
        db.commit()
        db.refresh(office_date)

        times = times + 1
    return "The office dates are updated!"


def get_all_dates_for_office_id(
        office_id: int,
        office_doctor_availability_id:int,
        db: Session):
    office_date_list = []
    office_dates = db.query(
        office_models.OfficeDate).filter(
        office_models.OfficeDate.office_id == office_id,
        office_models.OfficeDate.office_doctor_availability_id == office_doctor_availability_id).all()
    for office_date in office_dates:
        office_date_list.append(office_date)
    return office_date_list


def get_office_list_by_doctor_id(
        doctor_id: int,
        db: Session):
    offices = db.query(
        office_models.Office).filter(
        office_models.Office.doctor_id == doctor_id).all()
    office_list = []
    for office in offices:
        office_list.append(office)
    return office_list


def get_office_by_office_id(
        office_id: int,
        db: Session):
    office = db.query(
        office_models.Office).filter(
    office_models.Office.id == office_id).first()
    return office


def get_insurance_list_by_office_id(
        office_id: int,
        db: Session):
    insurance_list = []
    insurances = db.query(
        office_models.InNetworkInsurance).filter(
    office_models.InNetworkInsurance.office_id == office_id).all()
    print(insurances)
    for insurance in insurances:
        print(insurance)
        insurance_list.append(insurance)
    return insurance_list


def get_doctor_hospital_affiliation_list_by_office_id(
    db: Session,
        office_id: int,
):
    hospital_affiliation_list = []
    doctor_id = db.query(
        office_models.Office.doctor_id).filter(office_models.Office.id == office_id).first()[0]
    hospital_affiliations = db.query(
        doctor_models.HospitalAffiliation).filter(doctor_models.HospitalAffiliation.doctor_id == doctor_id).all()
    for hospital_affiliation in hospital_affiliations:
        hospital_affiliation_list.append(hospital_affiliation)
    return hospital_affiliation_list


def get_doctor_hospital_affiliation_name_by_office_id(
    db: Session,
        office_id: int,
):
    hospital_affiliation_id = db.query(
        office_models.Office.hospital_affiliation_id).filter(office_models.Office.id == office_id).first()[0]
    hospital_affiliation_name = db.query(
        doctor_models.HospitalAffiliation.hospital_name).filter(doctor_models.HospitalAffiliation.id == hospital_affiliation_id).first()[0]
    if hospital_affiliation_name:
        return hospital_affiliation_name


def get_office_doctor_availability_list_by_office_id(
        office_id: int,
        db: Session):
    office_doctor_availability_list = []
    office_doctor_availabilities = db.query(
        office_models.OfficeDoctorAvailability).filter(
    office_models.OfficeDoctorAvailability.office_id == office_id).all()
    for office_doctor_availability in office_doctor_availabilities:
        office_doctor_availability_list.append(office_doctor_availability)
    return office_doctor_availability_list


def get_office_id_patient_dates_converged(
        db: Session,
        patient_start_time: datetime,
        patient_end_time: datetime
):

    patient_office_dates_converged = db.query(
        office_models.OfficeDate.office_id).filter(
        office_models.OfficeDate.start_time == patient_start_time,
        office_models.OfficeDate.end_time == patient_end_time
    ).all()

    patient_office_id_list: list[int] = []

    for patient_office_date_converged_id in patient_office_dates_converged:
        patient_office_id_list.append(patient_office_date_converged_id[0])

    return patient_office_id_list


def get_office_dates_of_chosen_doctor(
        chosen_doctor_id: int,
        db: Session
):

    office_id = db.query(
        office_models.Office.id).filter(
        office_models.Office.doctor_id == chosen_doctor_id
    ).first()[0]

    chosen_doctor_office_dates = db.query(
        office_models.OfficeDate).filter(
        office_models.OfficeDate.office_id == office_id
    ).all()

    return chosen_doctor_office_dates
