from datetime import datetime

from app.core import hashing
from app.db.cruds import auth
from app.db.cruds.patient import create_patient
from app.db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.templating import Jinja2Templates
from app.schemas.schemas import PatientCreate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.routers.patients.forms import PatientCreateForm


templates = Jinja2Templates(directory="app/templates")
router = APIRouter(include_in_schema=False)


@router.get("/register/patient")
def register(request: Request):
    return templates.TemplateResponse("registration/patient_registration.html", {"request": request})


@router.post("/register/patient")
async def register(request: Request, db: Session = Depends(get_db)):
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
                patient = create_patient(patient=patient, db=db)
                return responses.RedirectResponse(
                    "/login/", status_code=status.HTTP_302_FOUND
                )  # default is post request, to use get request added status code 302
            except IntegrityError:
                form.__dict__.get("errors").append("Duplicate username or email")
                return templates.TemplateResponse("registration/patient_registration.html", form.__dict__)
        else:
            for error in error_list:
                form.__dict__.get("errors").append(error)
            return templates.TemplateResponse("registration/patient_registration.html", form.__dict__)
    return templates.TemplateResponse("registration/patient_registration.html", form.__dict__)



