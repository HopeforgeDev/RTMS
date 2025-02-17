from app.db.cruds.doctor import create_doctor, get_specialization_id_by_specialization_name, \
    create_doctor_specialization, create_qualification, create_hospital_affiliation, get_specialization_name_list
from app.db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.templating import Jinja2Templates
from app.schemas.schemas import DoctorCreate, SpecializationCreate, DoctorSpecializationCreate, QualificationCreate, \
    HospitalAffiliationCreate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.routers.doctors.forms import DoctorCreateForm
from app.core import hashing
from app.db.cruds import auth


templates = Jinja2Templates(directory="app/templates")
router = APIRouter(include_in_schema=False)


@router.get("/register/doctor")
def register(request: Request, db: Session = Depends(get_db)):
    specialization_name_list = get_specialization_name_list(db=db)
    return templates.TemplateResponse("registration/doctor_registration.html", {"request": request, "specialization_name_list": specialization_name_list})


@router.post("/register/doctor")
async def register(request: Request, db: Session = Depends(get_db)):
    form = DoctorCreateForm(request)
    await form.load_data()
    if await form.is_valid():

        error_list: list[str] = []
        hashed_secret = ""
        hashed_password = hashing.Hasher.get_password_hash(form.password)
        password = hashed_password
        pat = "@doctors.rtms.com"
        email_valid = auth.validate_email(email=form.email, user_type="doctor", pat=pat)
        user_full_name_list = auth.validate_full_name(
            first_name=form.first_name,
            middle_name=form.middle_name,
            last_name=form.last_name)

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
            try:

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

                for qualification_name, institute_name, procurement_year in zip(form.qualification_name_list, form.institute_name_list, form.procurement_year_list):
                    print(procurement_year)
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
                        hospital_affiliation=hospital_affiliation
                    )

                return responses.RedirectResponse(
                    "/login/", status_code=status.HTTP_302_FOUND
                )  # default is post request, to use get request added status code 302
            except IntegrityError:
                form.__dict__.get("errors").append("Duplicate email")
                return templates.TemplateResponse("registration/doctor_registration.html", form.__dict__)
        else:
            for error in error_list:
                form.__dict__.get("errors").append(error)
            return templates.TemplateResponse("registration/doctor_registration.html", form.__dict__)

    return templates.TemplateResponse("registration/doctor_registration.html", form.__dict__)
