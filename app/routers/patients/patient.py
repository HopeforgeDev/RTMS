from datetime import datetime
from http.client import HTTPException
from typing import Optional

import requests

from app.apis.version1.route_login import get_current_user_from_token
from urllib.parse import quote, unquote
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import responses, Query
from fastapi import status
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError

from app.db.cruds.appointment import get_appointment_list_by_patient_id, create_patient_appointment, \
    delete_appointment_by_id, get_doctor_list_by_specialization_name_filter, get_hospital_name_by_affiliation, get_office_with_hospital_info
from app.db.cruds.doctor import search_for_doctor_id_by_doctor_full_name, get_specialization_id_by_specialization_name, \
    get_specialization_name_list, get_doctor_id_list_by_specialization_name, get_doctor_list_by_specialization_name, \
    get_specialization_name_by_doctor_id, get_qualification_list_by_doctor_id, \
    get_doctor_hospital_affiliation_list_by_doctor_id, get_doctor
from app.db.cruds.office import get_office_list_by_doctor_id, get_all_dates_for_office_id, \
    get_office_doctor_availability_list_by_office_id
from app.db.cruds.patient import update_patient_by_id
from app.db.models import Patient, Doctor, appointment_models, doctor_models, office_models
from app.routers.appointments.forms import AppointmentCreateForm
from app.routers.patients.forms import PatientCreateForm, PatientEditForm, SpecializationChooseForm
from app.schemas.schemas import SpecializationChoose

from app.schemas import schemas
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core import hashing
from app.db.cruds import auth
from app.schemas.schemas import PatientCreate

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(include_in_schema=False)


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "general_pages/homepage.html", {"request": request}
    )


@router.get("/patient/dashboard/")
async def home(request: Request, db: Session = Depends(get_db)):
    error_list: list[str] = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        print(token)
        current_patient: Patient = get_current_user_from_token(token=param, db=db)
        if current_patient.user_type == "patient":

            return templates.TemplateResponse("patient/dashboard.html", status_code=status.HTTP_302_FOUND, context={"request": request, "current_patient": current_patient})
        else:
            error_list.append(
                "Your login expired, or you aren't logged in yet! Please,login and then retry"
            )
            return templates.TemplateResponse("/patient/dashboard.html",
                                              context={"request": request, "errors": error_list})
    except Exception as e:
        print(e)
        error_list.append(
            "You might not be logged in! Please,login and then retry"
        )
        return templates.TemplateResponse("/patient/dashboard.html", context={"request": request, "errors": error_list})


@router.get("/patient/profile_edit")
def patient_profile_edit(request: Request, db: Session = Depends(get_db)):
    error_list = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_patient: Patient = get_current_user_from_token(token=param, db=db)
        if current_patient.user_type == "patient":
            return templates.TemplateResponse("patient/profile_edit.html", {"request": request, "current_patient": current_patient})
        else:
            error_list.append(
                "Your login expired, or you aren't logged in yet! Please,login and then retry"
            )
            return templates.TemplateResponse("patient/profile_edit.html",
                                              {"request": request, "error_list": error_list})
    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
        return templates.TemplateResponse("patient/profile_edit.html", {"request": request, "error_list": error_list})


@router.post("/patient/profile_edit")
async def patient_profile_edit(request: Request, db: Session = Depends(get_db)):
    form = PatientEditForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(
        token
            )  # scheme will hold "Bearer" and param will hold actual token value
            current_patient: Patient = get_current_user_from_token(token=param, db=db)
            if current_patient.user_type == "patient":
                error_list: list[str] = []
                gender_bool: bool = False
                if form.gender == "Male":
                    gender_bool = True
                elif form.gender == "Female":
                    gender_bool = False
                else:
                    error = "Please, you need to select your gender!"
                    error_list.append(error)

                password = db.query(Patient.password).filter(Patient.id == current_patient.id).first()[0]
                pat = "@patients.rms.com"
                email_valid = auth.validate_email(email=form.email, user_type="patient", pat=pat)
                user_full_name_list = auth.validate_full_name(
                    first_name=form.first_name,
                    middle_name=form.middle_name,
                    last_name=form.last_name)

                if not email_valid:
                    error = f'Should not contain : !,@,#,$,%,^,&,*,(,),_,+,/,*,-,,~,.,?\nShould ends with: {pat}'
                    error_list.append(error)

                if auth.validate_date(start_date=None, end_date=None, start_datetime=None,
                                      end_datetime=None,
                                      past_date=datetime.strptime(form.date_of_birth, '%Y-%m-%d').date()):
                    error = "Please! enter your birth date precisely"
                    error_list.append(error)
                if len(error_list) == 0:
                    try:
                        patient = PatientCreate(
                            first_name=user_full_name_list[0],
                            middle_name=user_full_name_list[1],
                            last_name=user_full_name_list[2],
                            gender=gender_bool,
                            contact_number=form.contact_number,
                            length=form.length,
                            weight=form.weight,
                            date_of_birth=form.date_of_birth,
                            pathological_cases=form.pathological_cases,
                            surgeries=form.surgeries,
                            medicines=form.medicines,
                            permanent_health_symptoms=form.permanent_health_symptoms,
                            email=form.email,
                            password=password)
                        update_patient_by_id(current_patient.id, patient, db)
                        return responses.RedirectResponse(
                            "/patient/dashboard/", status_code=status.HTTP_302_FOUND
                        )
                    except IntegrityError:
                        form.__dict__.get("errors").append("Duplicate username or email")
                        return templates.TemplateResponse("patient/profile_edit.html", form.__dict__)
                else:
                    for error in error_list:
                        form.__dict__.get("errors").append(error)
                    return templates.TemplateResponse("patient/profile_edit.html", form.__dict__)
            else:
                form.__dict__.get("errors").append(
                    "Your login expired, or you aren't logged in yet! Please,login and then retry"
                )
                return templates.TemplateResponse("patient/profile_edit.html", form.__dict__)
        except Exception as e:
            print(e)
            form.__dict__.get("errors").append(
                "Your login expired, or you aren't logged in yet! Please,login and then retry"
            )
            return templates.TemplateResponse("patient/profile_edit.html", form.__dict__)
    return templates.TemplateResponse("patient/profile_edit.html", form.__dict__)


@router.get("/patient/appointment/choose_specialization/search")
def search_doctors_in_specialization(
    request: Request,
    db: Session = Depends(get_db),
    specialization: str = Query(...),  # Mandatory specialization
    name_query: Optional[str] = None
):
    try:
        # Authentication
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        current_patient = get_current_user_from_token(token=param, db=db)
        
        if current_patient.user_type != "patient":
            raise HTTPException(status_code=403, detail="Access denied")

        # Get base doctor list for the specialization
        doctor_list = get_doctor_list_by_specialization_name_filter(
            db=db, 
            specialization_name=specialization,
            name_filter=name_query
        )

        # Process offices and hospitals
        doctors_office_dict_list = []
        for doctor in doctor_list:
            print(doctor.id)
            offices = get_office_list_by_doctor_id(db=db, doctor_id=doctor.id)
            print(offices)
            doctors_office_dict_list.append({
                "doctor": doctor,
                "office_list": [
                    {
                        **office.__dict__,
                        "hospital_name": get_hospital_name_by_affiliation(
                            db=db, 
                            affiliation_id=office.hospital_affiliation_id
                        )
                    } for office in offices
                ]
            })

        return templates.TemplateResponse("patient/appointments_add.html", {
            "request": request,
            "current_patient": current_patient,
            "specialization_name": specialization,
            "doctors_office_dict_list": doctors_office_dict_list,
            "name_query": name_query
        })

    except Exception as e:
        print(f"Search error: {e}")
        return templates.TemplateResponse("patient/appointments_add.html", {
            "request": request, "errors": ["Error searching for doctors"]})

@router.get("/patient/appointments")
async def home(request: Request, db: Session = Depends(get_db)):
    error_list: list[str] = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        current_patient: Patient = get_current_user_from_token(token=param, db=db)
        
        if current_patient.user_type != "patient":
            return responses.RedirectResponse("/login")
            
        # Get appointments with related data in a single query
        appointments = db.query(
            appointment_models.Appointment,
            doctor_models.Doctor.first_name,
            doctor_models.Doctor.middle_name,
            doctor_models.Doctor.last_name,
            doctor_models.HospitalAffiliation.hospital_name
        ).join(
            office_models.Office,
            appointment_models.Appointment.office_id == office_models.Office.id
        ).join(
            doctor_models.Doctor,
            office_models.Office.doctor_id == doctor_models.Doctor.id
        ).join(
            doctor_models.HospitalAffiliation,
            office_models.Office.hospital_affiliation_id == doctor_models.HospitalAffiliation.id
        ).filter(
            appointment_models.Appointment.patient_id == current_patient.id
        ).all()

        # Process appointments with full names
        processed_appointments = []
        for appt, first, middle, last, hospital in appointments:
            processed_appointments.append({
                "appointment": appt,
                "doctor_name": f"{first} {middle} {last}".replace("  ", " "),
                "hospital_name": hospital
            })

        return templates.TemplateResponse(
            "patient/appointments.html",
            {
                "request": request,
                "current_patient": current_patient,
                "appointments": processed_appointments
            }
        )

    except Exception as e:
        print(f"Error: {e}")
        return templates.TemplateResponse(
            "patient/appointments.html",
            {"request": request, "error": "Error retrieving appointments"}
        )

@router.get("/patient/delete_appointment/{appointment_id}")
async def patient_delete_appointment(request: Request, appointment_id: int, db: Session = Depends(get_db)):
    error_list: list[str] = []
    try:
        token = request.cookies.get("access_token")
        print(token)
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_patient: Patient = get_current_user_from_token(token=param, db=db)
        if current_patient.user_type == "patient":
            result = delete_appointment_by_id(appointment_id, db)
            return responses.RedirectResponse(
                "/patient/appointments", status_code=status.HTTP_302_FOUND
            )
        else:
            error_list.append(
                "Your login expired, or you aren't logged in yet! Please,login and then retry"
            )
            return templates.TemplateResponse("patient/appointments.html", {"request": request, "errors": error_list})

    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
        return templates.TemplateResponse("patient/appointments.html", {"request": request, "errors": error_list})


@router.get("/patient/appointment/choose_specialization")
def patient_choose_specialization(request: Request, db: Session = Depends(get_db)):
    error_list: list[str] = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        current_patient: Patient = get_current_user_from_token(token=param, db=db)
        if current_patient.user_type == "patient":
            specialization_name_list = get_specialization_name_list(db=db)
            return templates.TemplateResponse("appointment/specializations.html", {
                "request": request,
                "current_patient": current_patient,
                "specialization_name_list": specialization_name_list,
                "errors": error_list  # Pass error_list even if empty
            })
        else:
            error_list.append("Your login expired, or you aren't logged in yet! Please, login and then retry")
            return templates.TemplateResponse("appointment/specializations.html", {
                "request": request,
                "errors": error_list
            })
    except Exception as e:
        print(e)
        error_list.append("Your login expired, or you aren't logged in yet! Please, login and then retry")
        return templates.TemplateResponse("appointment/specializations.html", {
            "request": request,
            "errors": error_list
        })


@router.post("/patient/appointment/choose_specialization")
async def handle_specialization_choice(request: Request, db: Session = Depends(get_db)):
    error_list: list[str] = []
    doctors_office_dict_list = []
    
    form = SpecializationChooseForm(request)
    await form.load_data()
    if not await form.is_valid():  # Form is NOT valid, return with errors and the form
        return templates.TemplateResponse("appointment/specializations.html", {
            "request": request,
            "errors": form.errors,  # Pass the form's errors
            "form": form,  # Pass the form object itself
            "specialization_name_list": get_specialization_name_list(db=db)
        })
    if await form.is_valid():
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(token)
            current_patient: Patient = get_current_user_from_token(token=param, db=db)
            if current_patient.user_type != "patient":
                error_list.append("Your login expired, or you aren't logged in yet! Please, login and then retry")
                return templates.TemplateResponse("appointment/specializations.html", {
                    "request": request,
                    "errors": error_list,
                    "specialization_name_list": get_specialization_name_list(db=db)
                })

            if current_patient.user_type == "patient":
                doctors_office_dict_list = []
                doctor_list = get_doctor_list_by_specialization_name(db=db, specialization_name=form.specialization_name)

                if isinstance(doctor_list, str):  # Check if doctor_list is a string (error message)
                    error_list.append(doctor_list)  # Add the error message to the error_list
                    return templates.TemplateResponse("appointment/specializations.html", {
                        "request": request,
                        "errors": error_list,
                        "specialization_name_list": get_specialization_name_list(db=db) # Important: reload specialization list
                    })

                for doctor in doctor_list:
                    # Get offices with hospital names
                    offices_with_hospitals = get_office_with_hospital_info(db, doctor.id)
                    
                    office_list = []
                    hospital_names = []
                    for office, hospital_name in offices_with_hospitals:
                        office.hospital_name = hospital_name  # Attach directly to office
                        office_list.append(office)
                        hospital_names.append(hospital_name)

                    doctors_office_dict_list.append({
                        "doctor": doctor,
                        "office_list": office_list,
                        "hospital_names": hospital_names
                    })

                return templates.TemplateResponse("patient/appointments_add.html", {
                    "request": request,
                    "current_patient": current_patient,
                    "specialization_name": form.specialization_name,
                    "doctors_office_dict_list": doctors_office_dict_list
                })

            else:
                error_list.append("Your login expired, or you aren't logged in yet! Please, login and then retry")
                return templates.TemplateResponse("appointment/specializations.html", {
                    "request": request,
                    "errors": error_list,
                    "specialization_name_list": get_specialization_name_list(db=db)
                })
        except Exception as e:
            print(e)
            error_list.append("Your login expired, or you aren't logged in yet! Please, login and then retry")
            return templates.TemplateResponse("appointment/specializations.html", {
                "request": request,
                "errors": error_list,
                "form": form,
                "specialization_name_list": get_specialization_name_list(db=db)
            })
    return templates.TemplateResponse("appointment/specializations.html", {
        "request": request,
        "errors": error_list,
        "specialization_name_list": get_specialization_name_list(db=db)
    })


@router.get("/patient/review_doctor/{doctor_id}")
async def home(request: Request, doctor_id: int, db: Session = Depends(get_db)):
    all_doctor_inform_dict = {}
    error_list: list[str] = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_patient: Patient = get_current_user_from_token(token=param, db=db)
        if current_patient.user_type == "patient":

            doctor = get_doctor(db=db, doctor_id=doctor_id)

            specialization_name = get_specialization_name_by_doctor_id(db=db, doctor_id=doctor_id)

            qualification_list = get_qualification_list_by_doctor_id(db=db, doctor_id=doctor_id)

            qualification_list_len = len(qualification_list)

            hospital_affiliation_list = get_doctor_hospital_affiliation_list_by_doctor_id(db=db, doctor_id=doctor_id)

            hospital_affiliation_list_len = len(hospital_affiliation_list)

            length_range = range(0, max(hospital_affiliation_list_len, qualification_list_len))

            qualification_list_range = range(0, qualification_list_len)
            hospital_affiliation_list_range = range(0, hospital_affiliation_list_len)
            all_doctor_inform_dict = {"doctor": doctor, "specialization_name": specialization_name,
                                      "qualification_list": qualification_list,
                                      "hospital_affiliation_list": hospital_affiliation_list,
                                      "qualification_list_len": qualification_list_len,
                                      "qualification_list_range": qualification_list_range,
                                      "hospital_affiliation_list_range": hospital_affiliation_list_range,
                                      "hospital_affiliation_list_len": hospital_affiliation_list_len,
                                      "length_range": length_range}
            return templates.TemplateResponse("appointment/review.html", status_code=status.HTTP_302_FOUND, context={"request": request, "all_doctor_inform_dict": all_doctor_inform_dict})
        else:
            error_list.append(
                "Your login expired, or you aren't logged in yet! Please,login and then retry"
            )
            return templates.TemplateResponse("/appointment/review.html",
                                              context={"request": request, "errors": error_list,
                                                       "all_doctor_inform_dict": all_doctor_inform_dict})
    except Exception as e:
        print(e)
        error_list.append(
            "You might not be logged in! Please,login and then retry"
        )
        return templates.TemplateResponse("/appointment/review.html", context={"request": request, "errors": error_list, "all_doctor_inform_dict": all_doctor_inform_dict})


@router.get("/patient/choose_doctor_office/{office_id}")
async def home(request: Request, office_id: int, db: Session = Depends(get_db)):
    office_date_list = []
    error_list: list[str] = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_patient: Patient = get_current_user_from_token(token=param, db=db)
        if current_patient.user_type == "patient":


            office_doctor_availability_list = get_office_doctor_availability_list_by_office_id(db=db, office_id=office_id)


            for office_doctor_availability in office_doctor_availability_list:
                for office_date in get_all_dates_for_office_id(db=db,
                                                            office_id=office_id,
                                                            office_doctor_availability_id=office_doctor_availability.id):
                    office_date_list.append(office_date)

            print(office_date_list)

            return templates.TemplateResponse("appointment/choose.html", status_code=status.HTTP_302_FOUND, context={"request": request, "current_patient": current_patient, "office_id":office_id, "office_doctor_availability_list":office_doctor_availability_list, "office_date_list": office_date_list})
        else:
            error_list.append(
                "Your login expired, or you aren't logged in yet! Please,login and then retry"
            )
            return templates.TemplateResponse("/appointment/choose.html",
                                              context={"request": request, "errors": error_list,
                                                       "office_date_list": office_date_list})
    except Exception as e:
        print(e)
        error_list.append(
            "You might not be logged in! Please,login and then retry"
        )
        return templates.TemplateResponse("/appointment/choose.html", context={"request": request, "errors": error_list, "office_date_list": office_date_list})


@router.post("/patient/choose_doctor_office/{office_id}")
async def home(request: Request, office_id: int, db: Session = Depends(get_db)):
    office_date_list = []
    error_list: list[str] = []
    form = AppointmentCreateForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(
                token
            )  # scheme will hold "Bearer" and param will hold actual token value
            current_patient: Patient = get_current_user_from_token(token=param, db=db)
            if current_patient.user_type == "patient":
                appointment = schemas.AppointmentCreate(
                    probable_start_time=form.probable_start_time,
                    actual_end_time=form.actual_end_time,
                    appointment_taken_date=form.appointment_taken_date
                )

                print(appointment)

                appointment_status_active_exists = db.query(
                    appointment_models.AppointmentStatus.id).filter(
                    appointment_models.AppointmentStatus.status == "active"
                ).first()
                if not appointment_status_active_exists:
                    appointment_status_active = appointment_models.AppointmentStatus(
                        id=1,
                        status="active"
                    )
                    db.add(appointment_status_active)
                    db.commit()
                    db.refresh(appointment_status_active)

                appointment_status_completed_exists = db.query(
                    appointment_models.AppointmentStatus.id).filter(
                    appointment_models.AppointmentStatus.status == "completed"
                ).first()
                if not appointment_status_completed_exists:
                    appointment_status_completed = appointment_models.AppointmentStatus(
                        id=2,
                        status="completed"
                    )
                    db.add(appointment_status_completed)
                    db.commit()
                    db.refresh(appointment_status_completed)

                appointment_status_canceled_exists = db.query(
                    appointment_models.AppointmentStatus.id).filter(
                    appointment_models.AppointmentStatus.status == "canceled"
                ).first()
                if not appointment_status_canceled_exists:
                    appointment_status_canceled = appointment_models.AppointmentStatus(
                        id=3,
                        status="canceled"
                    )
                    db.add(appointment_status_canceled)
                    db.commit()
                    db.refresh(appointment_status_canceled)

                appointment_status_active_id = db.query(
                    appointment_models.AppointmentStatus.id).filter(
                    appointment_models.AppointmentStatus.status == "active"
                ).first()[0]

                create_patient_appointment(appointment=appointment,
                                           office_id=office_id,
                                           patient_id=current_patient.id,
                                           appointment_status_id=appointment_status_active_id,
                                           db=db)

                return responses.RedirectResponse(
                    "/patient/appointments", status_code=status.HTTP_302_FOUND
                )
            else:
                form.__dict__.get("errors").append(
                    "Your login expired, or you aren't logged in yet! Please,login and then retry"
                )
                return templates.TemplateResponse("/appointment/choose.html", form.__dict__)
        except Exception as e:
            print(e)
            form.__dict__.get("errors").append(
                "Your login expired, or you aren't logged in yet! Please,login and then retry"
            )
            return templates.TemplateResponse("/appointment/choose.html", form.__dict__)
    return templates.TemplateResponse("/appointment/choose.html", form.__dict__)
