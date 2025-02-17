from typing import Optional

import requests

from app.apis.version1.route_login import get_current_user_from_token
from app.db.cruds.office import delete_office_doctor_availability_by_id, get_doctor_hospital_affiliation_name_by_office_id, get_office_list_by_doctor_id, create_office, delete_office_by_id, update_in_network_insurance, update_office_by_id, \
    create_office_date, create_doctor_availability, get_office_by_office_id, \
    get_office_doctor_availability_list_by_office_id, get_insurance_list_by_office_id, \
    get_doctor_hospital_affiliation_list_by_office_id, \
    update_doctor_availability_by_id, update_office_date_by_office_id, admit_in_network_insurance, \
    delete_insurance_by_office_id, create_office_geolocation
from app.db.models import Doctor, doctor_models
from app.db.models.admin_models import Admin
from app.db.cruds.doctor import create_doctor, create_specialization, get_doctor_hospital_affiliation_names_by_doctor_id, update_doctor_by_id, update_specialization_by_id, \
    delete_specialization_by_id, delete_doctor_by_id, get_specialization_name_list, \
    get_specialization_id_by_specialization_name, create_doctor_specialization, create_qualification, \
    create_hospital_affiliation, get_specialization_name_by_doctor_id, get_qualification_list_by_doctor_id, \
    get_doctor_hospital_affiliation_list_by_doctor_id, get_doctor_list
from app.db.cruds.doctor import get_doctors, get_specializations, get_doctor
from app.db.cruds.doctor import search_for_doctor_id_by_doctor_full_name
from app.db.models.appointment_models import Appointment
from app.db.models.office_models import Office
from app.db.models.patient_models import Patient
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError

from app.routers.admins.forms import SpecializationCreateForm
from app.routers.offices.forms import OfficeCreateForm
from app.schemas import schemas
from sqlalchemy.orm import Session, joinedload
from app.routers.doctors.forms import DoctorCreateForm
from app.db.session import get_db
from app.core import hashing
from app.db.cruds import auth
from app.schemas.schemas import DoctorCreate, DoctorSpecializationCreate, QualificationCreate, HospitalAffiliationCreate

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(include_in_schema=False)


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "general_pages/homepage.html", {"request": request}
    )


@router.get("/doctor/dashboard/")
async def home(request: Request, db: Session = Depends(get_db)):
    all_doctor_inform_dict = {}
    error_list: list[str] = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        print(token)
        current_doctor: Doctor = get_current_user_from_token(token=param, db=db)
        if current_doctor.user_type == "doctor":
            specialization_name = get_specialization_name_by_doctor_id(db=db, doctor_id=current_doctor.id)

            qualification_list = get_qualification_list_by_doctor_id(db=db, doctor_id=current_doctor.id)

            qualification_list_len = len(qualification_list)

            hospital_affiliation_list = get_doctor_hospital_affiliation_list_by_doctor_id(db=db, doctor_id=current_doctor.id)

            hospital_affiliation_list_len = len(hospital_affiliation_list)

            length_range = range(0, max(hospital_affiliation_list_len, qualification_list_len))

            qualification_list_range = range(0, qualification_list_len)
            hospital_affiliation_list_range = range(0, hospital_affiliation_list_len)
            all_doctor_inform_dict = {"current_doctor": current_doctor, "specialization_name": specialization_name,
                                      "qualification_list": qualification_list,
                                      "hospital_affiliation_list": hospital_affiliation_list,
                                      "qualification_list_len": qualification_list_len,
                                      "qualification_list_range": qualification_list_range,
                                      "hospital_affiliation_list_range": hospital_affiliation_list_range,
                                      "hospital_affiliation_list_len": hospital_affiliation_list_len,
                                      "length_range": length_range}
            return templates.TemplateResponse("doctor/dashboard.html", status_code=status.HTTP_302_FOUND, context={"request": request, "all_doctor_inform_dict": all_doctor_inform_dict})
        else:
            error_list.append(
                "Your login expired, or you aren't logged in yet! Please,login and then retry"
            )
            return templates.TemplateResponse("/doctor/dashboard.html",
                                              context={"request": request, "errors": error_list,
                                                       "all_doctor_inform_dict": all_doctor_inform_dict})
    except Exception as e:
        print(e)
        error_list.append(
            "You might not be logged in! Please,login and then retry"
        )
        return templates.TemplateResponse("/doctor/dashboard.html", context={"request": request, "errors": error_list, "all_doctor_inform_dict": all_doctor_inform_dict})


@router.get("/doctor/profile_edit")
def admin_edit_doctor(request: Request):
    return templates.TemplateResponse("doctor/profile_edit.html", {"request": request})


@router.post("/doctor/profile_edit")
async def doctor_profile_edit(request: Request, db: Session = Depends(get_db)):
    form = DoctorCreateForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(
                token
            )  # scheme will hold "Bearer" and param will hold actual token value
            current_doctor: Doctor = get_current_user_from_token(token=param, db=db)
            if current_doctor.user_type == "doctor":
                doctor = schemas.DoctorCreate(**form.__dict__)
                update_doctor_by_id(current_doctor.id, doctor, db)
                return responses.RedirectResponse(
                    "/doctor/dashboard/", status_code=status.HTTP_302_FOUND
                )
            else:
                form.__dict__.get("errors").append(
                    "Your login expired, or you aren't logged in yet! Please,login and then retry"
                )
                return templates.TemplateResponse("doctor/profile_edit.html", form.__dict__)
        except Exception as e:
            print(e)
            form.__dict__.get("errors").append(
                "Your login expired, or you aren't logged in yet! Please,login and then retry"
            )
            return templates.TemplateResponse("doctor/profile_edit.html", form.__dict__)
    return templates.TemplateResponse("doctor/profile_edit.html", form.__dict__)


@router.get("/search/")
def search(
    request: Request, db: Session = Depends(get_db), query: Optional[str] = None
):
    doctor_ids = search_for_doctor_id_by_doctor_full_name(db=db, searched_doctor_full_name=query)
    doctor_list = []
    for doctor_id in doctor_ids:
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        doctor_list.append(doctor)
    return templates.TemplateResponse(
        "general_pages/homepage.html", {"request": request, "doctor_list": doctor_list}
    )


@router.get("/doctor/offices")
async def home(request: Request, db: Session = Depends(get_db)):
    office_dict_list = {}
    office_list = []
    error_list: list[str] = []
    try:
        token = request.cookies.get("access_token")
        print(token)
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_doctor: Doctor = get_current_user_from_token(token=param, db=db)
        if current_doctor.user_type == "doctor":
            office_list = get_office_list_by_doctor_id(db=db, doctor_id=current_doctor.id)
            for office in office_list:
                office_doctor_availability_list = get_office_doctor_availability_list_by_office_id(db=db, office_id=office.id)
                office_name = get_doctor_hospital_affiliation_name_by_office_id(db=db, office_id=office.id)
                office_dict_list.update({office:[office_name, office_doctor_availability_list]})
            print(office_dict_list)
            return templates.TemplateResponse("/doctor/offices.html", context={"request": request, "errors": error_list, "current_doctor":current_doctor, "office_dict_list": office_dict_list, "office_list": office_list})
        else:
            error_list.append(
                "You might not be logged in, In case problem persists please contact us."
            )
            return templates.TemplateResponse("/doctor/offices.html", context={"request": request, "errors": error_list,
                                                                               "office_list": office_list})
    except Exception as e:
        print(e)
        error_list.append(
            "You might not be logged in, In case problem persists please contact us."
        )
        return templates.TemplateResponse("/doctor/offices.html", context={"request": request, "errors": error_list, "office_list": office_list})


@router.get("/doctor/create_office/")
def doctor_create_office(request: Request, db: Session = Depends(get_db)):
    error_list: list[str] = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_doctor: Doctor = get_current_user_from_token(token=param, db=db)
        if current_doctor.user_type == "doctor":

            hospital_affiliation_names = get_doctor_hospital_affiliation_names_by_doctor_id(db=db,
                                                                                          doctor_id=current_doctor.id)
            return templates.TemplateResponse("doctor/offices_add.html", {"request": request, "current_doctor": current_doctor, "hospital_affiliation_names": hospital_affiliation_names})
        else:
            error_list.append(
                "Your login expired, or you aren't logged in yet! Please,login and then retry"
            )
        return templates.TemplateResponse("doctor/offices_add.html",
                                          context={"request": request, "errors": error_list})
    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
    return templates.TemplateResponse("doctor/offices_add.html", context={"request": request, "errors": error_list})


@router.post("/doctor/create_office/")
async def doctor_create_office(request: Request, db: Session = Depends(get_db)):
    form = OfficeCreateForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(
                token
            )  # scheme will hold "Bearer" and param will hold actual token value
            current_doctor: Doctor = get_current_user_from_token(token=param, db=db)
            if current_doctor.user_type == "doctor":
                hospital_affiliation_list = get_doctor_hospital_affiliation_list_by_doctor_id(db=db, doctor_id=current_doctor.id)
                hospital_affiliation_count = int(form.hospital_affiliation_option)
                print(hospital_affiliation_count)
                i = 0
                hospital_affiliation_id = 0
                for hospital_affiliation in hospital_affiliation_list:
                    i = i+1
                    if hospital_affiliation_count == i:
                        print("hospital_affiliation.hospital_name", hospital_affiliation.hospital_name)
                        print("hospital_affiliation_count", hospital_affiliation_count)
                        hospital_affiliation_id = hospital_affiliation.id
                if hospital_affiliation_id != 0:

                    office = schemas.OfficeCreate(
                        doctor_id=current_doctor.id,
                        hospital_affiliation_id=hospital_affiliation_id,
                        time_slot_per_client_in_min=int(form.time_slot_per_client_in_min),
                        first_consultation_fee=int(form.first_consultation_fee),
                        followup_consultation_fee=int(form.followup_consultation_fee),
                        city=form.city,
                        country=form.country)
                    office = create_office(office=office, db=db)
                    for insurance_name in form.insurance_name_list:
                        insurance = schemas.InNetworkInsuranceCreate(insurance_name=insurance_name, office_id=office.id)
                        admit_in_network_insurance(db=db, in_network_insurance=insurance)
                    for date, start_time, end_time, reason_of_unavailability in zip(form.date_list, form.start_time_list, form.end_time_list, form.reason_of_unavailability_list):
                        is_available=False
                        print(date, start_time, end_time, reason_of_unavailability)
                        if reason_of_unavailability == "available":
                            is_available=True
                        office_doctor_availability = schemas.OfficeDoctorAvailabilityCreate(
                            office_id=office.id,
                            date=date,
                            start_time=start_time,
                            end_time=end_time,
                            is_available=is_available,
                            reason_of_unavailability=reason_of_unavailability
                        )
                        office_doctor_availability = create_doctor_availability(db=db, office_doctor_availability=office_doctor_availability)
                        create_office_date(db=db, office_id=office.id, office_doctor_availability_id=office_doctor_availability.id)

                    return responses.RedirectResponse(
                        "/doctor/offices", status_code=status.HTTP_302_FOUND
                    )
            else:
                form.__dict__.get("errors").append(
                    "Your login expired, or you aren't logged in yet! Please,login and then retry"
                )
                return templates.TemplateResponse("doctor/offices_add.html", form.__dict__)
        except Exception as e:
            print(e)
            form.__dict__.get("errors").append(
                "Your login expired, or you aren't logged in yet! Please,login and then retry"
            )
            return templates.TemplateResponse("doctor/offices_add.html", form.__dict__)
    return templates.TemplateResponse("doctor/offices_add.html", form.__dict__)


@router.get("/doctor/edit_office/{office_id}")
def doctor_edit_office(request: Request, office_id: int, db: Session = Depends(get_db)):
    error_list: list[str] = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_doctor: Doctor = get_current_user_from_token(token=param, db=db)
        if current_doctor.user_type == "doctor":
            hospital_affiliation_list = get_doctor_hospital_affiliation_list_by_office_id(db=db, office_id=office_id)
            hospital_affiliation_name_list = get_doctor_hospital_affiliation_names_by_office_id(db=db, office_id=office_id)
            office = get_office_by_office_id(db=db, office_id=office_id)
            office_doctor_availability_list = get_office_doctor_availability_list_by_office_id(db=db, office_id=office_id)
            insurance_list = get_insurance_list_by_office_id(db=db, office_id=office_id)
            print(insurance_list)
            return templates.TemplateResponse("doctor/offices_edit.html", {"request": request, "current_doctor":current_doctor, "office": office, "office_doctor_availability_list":office_doctor_availability_list, "insurance_list": insurance_list, "hospital_affiliation_name_list": hospital_affiliation_name_list})
        else:
            error_list.append(
                "Your login expired, or you aren't logged in yet! Please,login and then retry"
            )
            return templates.TemplateResponse("/doctor/offices_edit.html",
                                  context={"request": request, "errors": error_list})
    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
        return templates.TemplateResponse("/doctor/offices_edit.html", context={"request": request, "errors": error_list})


@router.post("/doctor/edit_office/{office_id}")
async def doctor_edit_office(request: Request, office_id: int, db: Session = Depends(get_db)):
    form = OfficeCreateForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(
                token
            )  # scheme will hold "Bearer" and param will hold actual token value
            current_doctor: Doctor = get_current_user_from_token(token=param, db=db)
            if current_doctor.user_type == "doctor":
                hospital_affiliation_list = get_doctor_hospital_affiliation_list_by_doctor_id(db=db, doctor_id=current_doctor.id)
                hospital_affiliation_count = int(form.hospital_affiliation_option)
                print(hospital_affiliation_count)
                i = 0
                hospital_affiliation_id = 0
                for hospital_affiliation in hospital_affiliation_list:
                    i = i+1
                    if hospital_affiliation_count == i:
                        hospital_affiliation_id = hospital_affiliation.id
                if hospital_affiliation_id != 0:

                    office = schemas.OfficeCreate(
                        doctor_id=current_doctor.id,
                        hospital_affiliation_id=hospital_affiliation_id,
                        time_slot_per_client_in_min=int(form.time_slot_per_client_in_min),
                        first_consultation_fee=int(form.first_consultation_fee),
                        followup_consultation_fee=int(form.followup_consultation_fee),
                        city=form.city,
                        country=form.country)
                    office = update_office_by_id(office_id=office_id, office=office, db=db)
                    # delete_insurance_by_office_id(db=db, office_id=office_id)
                    for insurance_name in form.insurance_name_list:
                        print(insurance_name)
                        insurance = schemas.InNetworkInsuranceCreate(insurance_name=insurance_name, office_id=office.id)
                        insurance_id = schemas.InNetworkInsurance(insurance_name=insurance_name).id
                        print(insurance)
                        update_in_network_insurance(insurance_id=insurance_id, office_id=office_id, db=db, in_network_insurance=insurance)
                    for date, start_time, end_time, reason_of_unavailability in zip(form.date_list, form.start_time_list, form.end_time_list, form.reason_of_unavailability_list):
                        is_available=False
                        if reason_of_unavailability == "available":
                            is_available=True
                        office_doctor_availability = schemas.OfficeDoctorAvailabilityCreate(
                            office_id=office.id,
                            date=date,
                            start_time=start_time,
                            end_time=end_time,
                            is_available=is_available,
                            reason_of_unavailability=reason_of_unavailability
                        )
                        office_doctor_availability = update_doctor_availability_by_id(office_id=office_doctor_availability.office_id, db=db, office_doctor_availability=office_doctor_availability)
                        print(office_doctor_availability)
                        if office_doctor_availability:
                            office_date = schemas.OfficeDateCreate(office_id=office_id, office_doctor_availability_id=office_doctor_availability.id)
                            update_office_date_by_office_id(db=db, office_date=office_date, office_id=office.id)

                        return responses.RedirectResponse(
                            "/doctor/offices", status_code=status.HTTP_302_FOUND
                        )
            else:
                form.__dict__.get("errors").append(
                    "Your login expired, or you aren't logged in yet! Please,login and then retry"
                )
                return templates.TemplateResponse("doctor/offices_edit.html", form.__dict__)
        except Exception as e:
            print(e)
            form.__dict__.get("errors").append(
                e
            )
            return templates.TemplateResponse("doctor/offices_edit.html", form.__dict__)
    return templates.TemplateResponse("doctor/offices_edit.html", form.__dict__)


@router.get("/doctor/delete_office/{office_doctor_availability_id}")
async def doctor_delete_office(request: Request, office_doctor_availability_id: int, db: Session = Depends(get_db)):
    error_list: list[str] = []
    try:
        token = request.cookies.get("access_token")
        print(token)
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_doctor: Doctor = get_current_user_from_token(token=param, db=db)
        if current_doctor.user_type == "doctor":
            result = delete_office_doctor_availability_by_id(office_doctor_availability_id, db)
            return responses.RedirectResponse(
                "/doctor/offices", status_code=status.HTTP_302_FOUND
            )
        else:
            error_list.append(
                "Your login expired, or you aren't logged in yet! Please,login and then retry"
            )
            return templates.TemplateResponse("doctor/offices.html", {"request": request, "errors": error_list})

    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
        return templates.TemplateResponse("doctor/offices.html", {"request": request, "errors": error_list})


@router.get("/doctor/patients")
def doctor_patients(
    request: Request,
    db: Session = Depends(get_db)
):
    patients_data = []
    try:
        token = request.cookies.get("access_token")
        print(token)
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_doctor: Doctor = get_current_user_from_token(token=param, db=db)
        if current_doctor.user_type == "doctor":
        # Get all appointments for this doctor with related data
            office_list = get_office_list_by_doctor_id(db=db, doctor_id=current_doctor.id)
            for office in office_list:
                appointments = db.query(Appointment).filter(Appointment.office_id == office.id).all()
                for appointment in appointments:
                    patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
                    # hospital_affiliation_names = get_hospital_affiliation_names_by_patient_id_and_office_id(db=db, patient_id=patient.id, office_id=office.id)
                    patients_data.append({"appointment": appointment, "patient": patient, "office": office})
            return templates.TemplateResponse(
                "doctor/patients.html",
                {
                    "request": request,
                    "current_doctor": current_doctor,
                    "patients": patients_data
                }
            )

    except Exception as e:
        print(f"Error fetching patients: {e}")
        return templates.TemplateResponse(
            "doctor/patients.html",
            {
                "request": request,
                "error": "Error loading patient data"
            }
        )
