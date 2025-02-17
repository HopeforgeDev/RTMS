from datetime import datetime
from typing import Optional
from app.apis.version1.route_login import get_current_user_from_token
from app.db.cruds.patient import get_patient, get_patient_list, get_patients, create_patient, update_patient_by_id, delete_patient_by_id, \
    deactivate_patient_by_id, activate_patient_by_id
from app.db.models import Doctor
from app.db.models.admin_models import Admin
from app.db.cruds.admin import update_admin_by_id
from app.db.cruds.doctor import create_doctor, create_specialization, update_doctor_by_id, update_specialization_by_id, \
    delete_specialization_by_id, delete_doctor_by_id, get_specialization_name_list, \
    get_specialization_id_by_specialization_name, create_doctor_specialization, create_qualification, \
    create_hospital_affiliation, get_doctor_list, get_specialization_name_by_doctor_id, \
    get_qualification_list_by_doctor_id, get_doctor_hospital_affiliation_list_by_doctor_id, deactivate_doctor_by_id, \
    activate_doctor_by_id
from app.db.cruds.doctor import get_doctors, get_specializations, get_doctor
from app.db.cruds.doctor import search_for_doctor_id_by_doctor_full_name
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError

from app.routers.admins.forms import AdminCreateForm, SpecializationCreateForm
from app.routers.patients.forms import PatientCreateForm
from app.schemas import schemas
from sqlalchemy.orm import Session
from app.routers.doctors.forms import DoctorCreateForm
from app.db.session import get_db
from app.core import hashing
from app.db.cruds import auth
from app.schemas.schemas import DoctorCreate, DoctorSpecializationCreate, QualificationCreate, \
    HospitalAffiliationCreate, PatientCreate

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(include_in_schema=False)


@router.get("/")
async def home(request: Request):
    register = True
    all = True
    return templates.TemplateResponse("general_pages/homepage.html", {"request": request, "register": register, "all": all})


@router.get("/admin/dashboard/")
async def home(request: Request, db: Session = Depends(get_db)):
    error_list: list[str] = []
    token = request.cookies.get("access_token")
    print(request.cookies)

    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_admin: Admin = get_current_user_from_token(token=param, db=db)
        print(current_admin)
        return templates.TemplateResponse("/admin/dashboard.html", status_code=status.HTTP_302_FOUND, context={"request": request, "current_admin": current_admin, "errors": error_list})

    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
        return templates.TemplateResponse("/admin/dashboard.html", context={"request": request, "errors": error_list})


@router.get("/admin/doctors")
async def home(request: Request, db: Session = Depends(get_db)):
    doctor_list = get_doctor_list(db=db)
    all_doctors_inform_list = []
    error_list = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_admin: Admin = get_current_user_from_token(token=param, db=db)
        for doctor in doctor_list:
            specialization_name = get_specialization_name_by_doctor_id(db=db, doctor_id=doctor.id)

            qualification_list = get_qualification_list_by_doctor_id(db=db, doctor_id=doctor.id)

            qualification_list_len = len(qualification_list)

            hospital_affiliation_list = get_doctor_hospital_affiliation_list_by_doctor_id(db=db, doctor_id=doctor.id)

            hospital_affiliation_list_len = len(hospital_affiliation_list)

            length_range = range(0, max(hospital_affiliation_list_len, qualification_list_len))

            all_doctor_inform_dict = {"doctor": doctor, "specialization_name": specialization_name, "qualification_list": qualification_list, "hospital_affiliation_list": hospital_affiliation_list, "qualification_list_len": qualification_list_len, "hospital_affiliation_list_len": hospital_affiliation_list_len, "length_range": length_range}
            all_doctors_inform_list.append(all_doctor_inform_dict)

        return templates.TemplateResponse("admin/doctors.html", status_code=status.HTTP_302_FOUND,
                                          context={
                                              "request": request,
                                              "all_doctors_inform_list": all_doctors_inform_list,
                                                "current_admin": current_admin,
                                          }
                                            )
    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
        return templates.TemplateResponse("/admin/doctors.html", context={"request": request, "errors": error_list})


@router.get("/admin/create_doctor/")
def admin_create_doctor(request: Request, db: Session = Depends(get_db)):
    error_list = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_admin: Admin = get_current_user_from_token(token=param, db=db)
        specialization_name_list = get_specialization_name_list(db=db)
        return templates.TemplateResponse("admin/doctors_add.html", {"request": request, "current_admin": current_admin,
                                                                     "specialization_name_list": specialization_name_list})
    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
        return templates.TemplateResponse("/admin/dashboard.html", context={"request": request, "errors": error_list})


@router.post("/admin/create_doctor/")
async def admin_create_doctor(request: Request, db: Session = Depends(get_db)):
    form = DoctorCreateForm(request)
    await form.load_data()

    error_list: list[str] = []

    if await form.is_valid():

        try:
            hashed_secret = ""
            hashed_password = hashing.Hasher.get_password_hash(form.password)
            password = hashed_password
            pat = "@doctors.rtms.com"
            email_valid = auth.validate_email(email=form.email, user_type="doctor", pat=pat)
            user_full_name_list = auth.validate_full_name(
                first_name=form.first_name,
                middle_name=form.middle_name,
                last_name=form.last_name)
            j_list: list[str] = []
            for j in range(0, 2):
                j_list.append(f'qualification_name_{j}')
            print(j_list)
            if not email_valid:
                error = f'Should not contain : !,@,#,$,%,^,&,*,(,),_,+,/,*,-,,~,.,?\nShould ends with: {pat}'
                error_list.append(error)

            secret_valid = auth.validate_secret(
                secret_to_validate=form.secret_for_doctor,
                secret="Iam the secret, you cannot know me! only if you are a doctor")
            if type(secret_valid) == bool:
                error = "Incorrect Secret"
                error_list.append(error)
            else:
                hashed_secret = secret_valid

            if len(error_list) == 0:

                doctor = DoctorCreate(
                    first_name=user_full_name_list[0],
                    middle_name=user_full_name_list[1],
                    last_name=user_full_name_list[2],
                    email=form.email,
                    password=password,
                    secret_for_doctor=hashed_secret,
                    professional_statement=form.professional_statement,
                    practicing_from=form.practicing_from)

                doctor = create_doctor(doctor=doctor, db=db)

                specialization = DoctorSpecializationCreate(
                    doctor_id=doctor.id,
                    specialization_id=get_specialization_id_by_specialization_name(
                        db=db,
                        specialization_name=form.specialization_name)
                )

                specialization = create_doctor_specialization(
                    db=db,
                    specialization=specialization
                )
                print(form.qualification_name_list)

                for qualification_name, institute_name, procurement_year in zip(form.qualification_name_list,
                                                                                form.institute_name_list,
                                                                                form.procurement_year_list):
                    qualification = QualificationCreate(
                        doctor_id=doctor.id,
                        qualification_name=qualification_name,
                        institute_name=institute_name,
                        procurement_year=procurement_year
                    )

                    qualification = create_qualification(
                        db=db,
                        qualification=qualification
                    )

                for hospital_name, city, country, start_date, end_date in zip(form.hospital_name_list,
                                                                              form.city_list,
                                                                              form.country_list,
                                                                              form.start_date_list,
                                                                              form.end_date_list,
                                                                              ):

                    if auth.validate_date(start_date=start_date, end_date=None, start_datetime=None,
                                          end_datetime=None, past_date=None):
                        error = "Please! enter your start date precisely"
                        error_list.append(error)

                    elif auth.validate_date(start_date=None, end_date=end_date, start_datetime=None,
                                            end_datetime=None, past_date=None):
                        error = "Please! enter your end date precisely"
                        error_list.append(error)

                    elif auth.validate_date(start_date=start_date, end_date=end_date, start_datetime=None,
                                            end_datetime=None, past_date=None):
                        error = "Be aware! start date > end date.\n Please! enter them precisely"
                        error_list.append(error)

                    hospital_affiliation = HospitalAffiliationCreate(
                        doctor_id=doctor.id,
                        hospital_name=hospital_name,
                        city=city,
                        country=country,
                        start_date=start_date,
                        end_date=end_date
                    )

                    hospital_affiliation = create_hospital_affiliation(
                        db=db,
                        hospital_affiliation=hospital_affiliation)

                return responses.RedirectResponse(
                    "/admin/doctors", status_code=status.HTTP_302_FOUND
                )
            else:
                form.__dict__.get("errors").append(error_list)
                return templates.TemplateResponse("admin/doctors_add.html", form.__dict__)
        except IntegrityError:
            form.__dict__.get("errors").append("Duplicate email")
            return templates.TemplateResponse("admin/doctors_add.html", form.__dict__)
    else:
        for error in error_list:
            form.__dict__.get("errors").append(error)
        return templates.TemplateResponse("admin/doctors_add.html", form.__dict__)


@router.get("/admin/edit_doctor/{doctor_id}")
def admin_edit_doctor(request: Request, db: Session = Depends(get_db)):
    error_list = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_admin: Admin = get_current_user_from_token(token=param, db=db)
        return templates.TemplateResponse("admin/doctors_edit.html", {"request": request, "current_admin": current_admin})
    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
        return templates.TemplateResponse("/admin/dashboard.html", context={"request": request, "errors": error_list})


@router.post("/admin/edit_doctor/{doctor_id}")
async def admin_edit_doctor(request: Request, doctor_id: int, db: Session = Depends(get_db)):
    form = DoctorCreateForm(request)
    await form.load_data()
    if await form.is_valid():
        try:

            doctor = schemas.DoctorCreate(**form.__dict__)
            update_doctor_by_id(doctor_id, doctor, db)
            return responses.RedirectResponse(
                "/admin/doctors", status_code=status.HTTP_302_FOUND
            )
        except Exception as e:
            print(e)
            form.__dict__.get("errors").append(
                "Your login expired, or you aren't logged in yet! Please,login and then retry"
            )
            return templates.TemplateResponse("admin/doctors_edit.html", form.__dict__)
    return templates.TemplateResponse("admin/doctors_edit.html", form.__dict__)

@router.get("/admin/edit_profile")
def admin_edit_admin(request: Request, db: Session = Depends(get_db)):
    error_list = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_admin: Admin = get_current_user_from_token(token=param, db=db)
        return templates.TemplateResponse("admin/profile_edit.html", {"request": request, "current_admin": current_admin})
    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
        return templates.TemplateResponse("/admin/dashboard.html", context={"request": request, "errors": error_list})


@router.post("/admin/edit_profile")
async def admin_edit_profile(request: Request, db: Session = Depends(get_db)):
    form = AdminCreateForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(
                token
            )  # scheme will hold "Bearer" and param will hold actual token value
            current_admin: Admin = get_current_user_from_token(token=param, db=db)
            if current_admin.user_type == "admin":
                error_list: list[str] = []
                gender_bool: bool = False
                if form.gender == "Male":
                    gender_bool = True
                elif form.gender == "Female":
                    gender_bool = False
                else:
                    error = "Please, you need to select your gender!"
                    error_list.append(error)

                password = db.query(Admin.password).filter(Admin.id == current_admin.id).first()[0]
                pat = "@patients.rms.com"
                email_valid = auth.validate_email(email=form.email, user_type="admin", pat=pat)
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
                        admin = schemas.AdminCreate(**form.__dict__)
                        update_admin_by_id(current_admin.id, admin, db)
                        return responses.RedirectResponse(
                            "/admin/dashboard", status_code=status.HTTP_302_FOUND
                        )
                    except IntegrityError:
                        form.__dict__.get("errors").append("Duplicate username or email")
                        return templates.TemplateResponse("admin/profile_edit.html", form.__dict__)
                else:
                    for error in error_list:
                        form.__dict__.get("errors").append(error)
                    return templates.TemplateResponse("admin/profile_edit.html", form.__dict__)
            else:
                form.__dict__.get("errors").append(
                    "Your login expired, or you aren't logged in yet! Please,login and then retry"
                )
                return templates.TemplateResponse("admin/profile_edit.html", form.__dict__)
        except Exception as e:
            print(e)
            form.__dict__.get("errors").append(
                "Your login expired, or you aren't logged in yet! Please,login and then retry"
            )
            return templates.TemplateResponse("admin/profile_edit.html", form.__dict__)
    return templates.TemplateResponse("admin/profile_edit.html", form.__dict__)


@router.get("/admin/deactivate_doctor/{doctor_id}")
def admin_edit_doctor(request: Request):
    error_list = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_admin: Admin = get_current_user_from_token(token=param, db=db)
        return templates.TemplateResponse("admin/doctors_edit.html", {"request": request, "current_admin": current_admin})
    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
    return templates.TemplateResponse("admin/doctors.html", {"request": request, "errors": error_list})


@router.post("/admin/deactivate_doctor/{doctor_id}")
async def admin_deactivate_doctor(request: Request, doctor_id: int, db: Session = Depends(get_db)):
    error_list: list[str] = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_admin: Admin = get_current_user_from_token(token=param, db=db)
        deactivate_doctor_by_id(db=db, doctor_id=doctor_id)
        return responses.RedirectResponse(
            "/admin/doctors", status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
        return templates.TemplateResponse("admin/doctors.html", {"request": request, "errors": error_list})


@router.get("/admin/activate_doctor/{doctor_id}")
def admin_edit_doctor(request: Request):
    return templates.TemplateResponse("admin/doctors.html", {"request": request})


@router.post("/admin/activate_doctor/{doctor_id}")
async def admin_activate_doctor(request: Request, doctor_id: int, db: Session = Depends(get_db)):
    error_list: list[str] = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_admin: Admin = get_current_user_from_token(token=param, db=db)
        activate_doctor_by_id(db=db, doctor_id=doctor_id)
        return responses.RedirectResponse(
            "/admin/doctors", status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
        return templates.TemplateResponse("admin/doctors.html", {"request": request, "errors": error_list})


@router.get("/admin/delete_doctor/{doctor_id}")
async def admin_delete_doctor(request: Request, doctor_id: int, db: Session = Depends(get_db)):
    error_list: list[str] = []
    try:
        token = request.cookies.get("access_token")
        print(token)
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        print(param)
        current_admin: Admin = get_current_user_from_token(token=param, db=db)
        print(current_admin)
        result = delete_doctor_by_id(doctor_id, db)
        print(result)
        return responses.RedirectResponse(
            "/admin/doctors", status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
        return templates.TemplateResponse("admin/doctors.html", {"request": request, "errors": error_list})


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


@router.get("/admin/specializations")
async def home(request: Request, db: Session = Depends(get_db)):
    error_list: list[str] = []
    try:
        token = request.cookies.get("access_token")
        print(token)
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        print(param)
        current_admin: Admin = get_current_user_from_token(token=param, db=db)
        specializations = get_specializations(db=db)
        return templates.TemplateResponse(
            "admin/specializations.html", {"request": request, "current_admin": current_admin, "specializations": specializations}
        )
    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
        return templates.TemplateResponse("/admin/specializations.html", context={"request": request, "errors": error_list})


@router.get("/admin/create_specialization/")
def admin_create_specialization(request: Request, db: Session = Depends(get_db)):
    error_list = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_admin: Admin = get_current_user_from_token(token=param, db=db)
        return templates.TemplateResponse("admin/specializations_add.html", {"request": request, "current_admin": current_admin})
    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
        return templates.TemplateResponse("/admin/specializations_add.html", context={"request": request, "errors": error_list})


@router.post("/admin/create_specialization/")
async def admin_create_specialization(request: Request, db: Session = Depends(get_db)):
    form = SpecializationCreateForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(
                token
            )  # scheme will hold "Bearer" and param will hold actual token value
            current_admin: Admin = get_current_user_from_token(token=param, db=db)
            specialization = schemas.SpecializationCreate(**form.__dict__)
            specialization = create_specialization(specialization=specialization, db=db)
            return responses.RedirectResponse(
                "/admin/specializations", status_code=status.HTTP_302_FOUND
            )
        except Exception as e:
            print(e)
            form.__dict__.get("errors").append(
                "Your login expired, or you aren't logged in yet! Please,login and then retry"
            )
            return templates.TemplateResponse("admin/specializations_add.html", form.__dict__)
    return templates.TemplateResponse("admin/specializations_add.html", form.__dict__)


@router.get("/admin/edit_specialization/{specialization_id}")
def admin_edit_specialization(request: Request, db: Session = Depends(get_db)):
    error_list = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_admin: Admin = get_current_user_from_token(token=param, db=db)
        return templates.TemplateResponse("admin/specializations_edit.html", {"request": request, "current_admin": current_admin})
    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
        return templates.TemplateResponse("admin/specializations_edit.html", {"request": request, "errors": error_list})


@router.post("/admin/edit_specialization/{specialization_id}")
async def admin_edit_specialization(request: Request, specialization_id: int, db: Session = Depends(get_db)):
    form = SpecializationCreateForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(
                token
            )  # scheme will hold "Bearer" and param will hold actual token value
            current_admin: Admin = get_current_user_from_token(token=param, db=db)
            specialization = schemas.SpecializationCreate(**form.__dict__)
            update_specialization_by_id(specialization_id, specialization, db)
            return responses.RedirectResponse(
                "/admin/specializations", status_code=status.HTTP_302_FOUND
            )
        except Exception as e:
            print(e)
            form.__dict__.get("errors").append(
                "Your login expired, or you aren't logged in yet! Please,login and then retry"
            )
            return templates.TemplateResponse("admin/specializations_edit.html", form.__dict__)
    return templates.TemplateResponse("admin/specializations_edit.html", form.__dict__)


@router.get("/admin/delete_specialization/{specialization_id}")
async def admin_delete_specialization(request: Request, specialization_id: int, db: Session = Depends(get_db)):
    error_list: list[str] = []
    try:
        token = request.cookies.get("access_token")
        print(token)
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        print(param)
        current_admin: Admin = get_current_user_from_token(token=param, db=db)
        print(current_admin)
        result = delete_specialization_by_id(specialization_id, db)
        print(result)
        return responses.RedirectResponse(
            "/admin/specializations", status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
        return templates.TemplateResponse("admin/specializations.html", {"request": request, "errors": error_list})


@router.get("/admin/patients")
async def home(request: Request, db: Session = Depends(get_db)):
    all_patients_inform_list = get_patient_list(db=db)

    error_list: list[str] = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        print(param)
        current_admin: Admin = get_current_user_from_token(token=param, db=db)
        return templates.TemplateResponse(
            "admin/patients.html", {"request": request, "all_patients_inform_list": all_patients_inform_list, "current_admin": current_admin}
        )
    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
        return templates.TemplateResponse("/admin/patients.html", context={"request": request, "errors": error_list})


@router.get("/admin/create_patient/")
def admin_create_patient(request: Request, db: Session = Depends(get_db)):
    error_list: list[str] = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        print(param)
        current_admin: Admin = get_current_user_from_token(token=param, db=db)
        patients = get_patients(db=db)
        return templates.TemplateResponse(
            "admin/patients_add.html", {"request": request, "patients": patients, "current_admin": current_admin}
        )
    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
        return templates.TemplateResponse("/admin/patients_add.html", context={"request": request, "errors": error_list})


@router.post("/admin/create_patient/")
async def admin_create_patient(request: Request, db: Session = Depends(get_db)):
    form = PatientCreateForm(request)
    await form.load_data()

    error_list: list[str] = []

    if await form.is_valid():

        try:

            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(
                token
            )  # scheme will hold "Bearer" and param will hold actual token value
            current_admin: Admin = get_current_user_from_token(token=param, db=db)
            if not current_admin:
                error = "Your login expired, or you aren't logged in yet! Please,login and then retry"

                error_list.append(error)

            hashed_secret = ""
            gender_bool: bool = False
            if form.gender == "Male":
                gender_bool = True
            elif form.gender == "Female":
                gender_bool = False
            else:
                error = "Please, you need to select your gender!"
                error_list.append(error)
            hashed_password = hashing.Hasher.get_password_hash(form.password)
            password = hashed_password
            pat = "@patients.rtms.com"
            email_valid = auth.validate_email(email=form.email, user_type="patient", pat=pat)
            user_full_name_list = auth.validate_full_name(
                first_name=form.first_name,
                middle_name=form.middle_name,
                last_name=form.last_name)

            if not email_valid:
                error = f'Should not contain : !,@,#,$,%,^,&,*,(,),_,+,/,*,-,,~,.,?\nShould ends with: {pat}'
                error_list.append(error)

            if len(error_list) == 0:
                patient = PatientCreate(
                    first_name=user_full_name_list[0],
                    middle_name=user_full_name_list[1],
                    last_name=user_full_name_list[2],
                    contact_number=form.contact_number,
                    date_of_birth=form.date_of_birth,
                    weight=form.weight,
                    length=form.length,
                    gender=gender_bool,
                    medicines=form.medicines,
                    pathological_cases=form.pathological_cases,
                    permanent_health_symptoms=form.permanent_health_symptoms,
                    surgeries=form.surgeries,
                    email=form.email,
                    password=password)

                patient = create_patient(patient=patient, db=db)
                return responses.RedirectResponse(
                    "/admin/patients", status_code=status.HTTP_302_FOUND
                )
        except Exception as e:
            print(e)
            form.__dict__.get("errors").append(
                "Your login expired, or you aren't logged in yet! Please,login and then retry"
            )
            return templates.TemplateResponse("admin/patients_add.html", form.__dict__)
    return templates.TemplateResponse("admin/patients_add.html", form.__dict__)


@router.get("/admin/edit_patient/{patient_id}")
def admin_edit_patient(request: Request, patient_id: int, db: Session = Depends(get_db)):
    error_list: list[str] = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_admin: Admin = get_current_user_from_token(token=param, db=db)
        current_patient = get_patient(db=db, patient_id=patient_id)
        return templates.TemplateResponse(
            "admin/patients_edit.html", {"request": request, "current_patient": current_patient, "current_admin": current_admin}
        )
    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
        return templates.TemplateResponse("admin/patients_edit.html", context={"request": request, "errors": error_list})


@router.post("/admin/edit_patient/{patient_id}")
async def admin_edit_patient(request: Request, patient_id: int, db: Session = Depends(get_db)):
    form = PatientCreateForm(request)
    await form.load_data()
    if await form.is_valid():

        error_list: list[str] = []
        gender_bool: bool = False
        if form.gender == "Male":
            gender_bool = True
        elif form.gender == "Female":
            gender_bool = False
        else:
            error = "Please, you need to select your gender!"
            error_list.append(error)
        hashed_password = hashing.Hasher.get_password_hash(form.password)
        password = hashed_password
        pat = "@patients.rtms.com"
        email_valid = auth.validate_email(email=form.email, user_type="patient", pat=pat)
        user_full_name_list = auth.validate_full_name(
            first_name=form.first_name,
            middle_name=form.middle_name,
            last_name=form.last_name)

        if not email_valid:
            error = f'Should not contain : !,@,#,$,%,^,&,*,(,),_,+,/,*,-,,~,.,?\nShould ends with: {pat}'
            error_list.append(error)

        if auth.validate_date(start_date=None, end_date=None, start_datetime=None,
                              end_datetime=None, past_date=datetime.strptime(form.date_of_birth, '%Y-%m-%d').date()):
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
                patient = update_patient_by_id(patient_id=patient_id, patient=patient, db=db)
                return responses.RedirectResponse(
                    "/admin/patients", status_code=status.HTTP_302_FOUND
                )  # default is post request, to use get request added status code 302
            except IntegrityError:
                form.__dict__.get("errors").append("Duplicate username or email")
                return templates.TemplateResponse("admin/patients_edit.html", form.__dict__)
        else:
            for error in error_list:
                form.__dict__.get("errors").append(error)
            return templates.TemplateResponse("admin/patients_edit.html", form.__dict__)
    return templates.TemplateResponse("admin/patients_edit.html", form.__dict__)


@router.get("/admin/deactivate_patient/{patient_id}")
def admin_deactivate_patient(request: Request, patient_id: int, db: Session = Depends(get_db)):
    error_list: list[str] = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_admin: Admin = get_current_user_from_token(token=param, db=db)
        current_patient = get_patient(db=db, patient_id=patient_id)
        deactivate_patient_by_id(db=db, patient_id=current_patient.id)
        return responses.RedirectResponse(
            "/admin/patients", status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
        return templates.TemplateResponse("admin/patients.html", context={"request": request, "errors": error_list})


@router.get("/admin/activate_patient/{patient_id}")
def admin_activate_patient(request: Request, patient_id: int, db: Session = Depends(get_db)):
    error_list: list[str] = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_admin: Admin = get_current_user_from_token(token=param, db=db)
        current_patient = get_patient(db=db, patient_id=patient_id)
        activate_patient_by_id(db=db, patient_id=current_patient.id)
        return responses.RedirectResponse(
            "/admin/patients", status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        print(e)
        error_list.append(
            "Your login expired, or you aren't logged in yet! Please,login and then retry"
        )
        return templates.TemplateResponse("admin/patients.html", context={"request": request, "errors": error_list})


@router.get("/logout")
async def logout(request: Request):
    # Create redirect response to login page
    response = responses.RedirectResponse(
        url="/login/", 
        status_code=status.HTTP_302_FOUND
    )
    
    # Remove the access_token cookie by setting expiration immediately
    response.delete_cookie(
        key="access_token",
        path="/",  # Match the path where cookie was set
        secure=False,  
        samesite="Lax"
    )
        
    return response
