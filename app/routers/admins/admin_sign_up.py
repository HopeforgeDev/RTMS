from app.db.cruds.admin import create_admin
from app.db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.templating import Jinja2Templates
from app.schemas.schemas import AdminCreate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.routers.admins.forms import AdminCreateForm
from app.core import hashing
from app.db.cruds import auth


templates = Jinja2Templates(directory="app/templates")
router = APIRouter(include_in_schema=False)


@router.get("/register")
def register(request: Request):
    register = True
    all = False
    return templates.TemplateResponse("general_pages/homepage.html", {"request": request, "register": register, "all": all})


@router.get("/register/admin")
def register(request: Request):
    return templates.TemplateResponse("registration/admin_registration.html", {"request": request})


@router.post("/register/admin")
async def register(request: Request, db: Session = Depends(get_db)):
    form = AdminCreateForm(request)
    await form.load_data()
    if await form.is_valid():

        error_list: list[str] = []
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
        pat = "@admins.rtms.com"
        email_valid = auth.validate_email(email=form.email, user_type="admin", pat=pat)
        user_full_name_list = auth.validate_full_name(
            first_name=form.first_name,
            middle_name=form.middle_name,
            last_name=form.last_name)

        if not email_valid:
            error = f'Should not contain : !,@,#,$,%,^,&,*,(,),_,+,/,*,-,,~,.,?\nShould ends with: {pat}'
            error_list.append(error)

        secret_valid = auth.validate_secret(
            secret_to_validate=form.secret_for_administration,
            secret="Iam the secret, you cannot know me! only if you are an admin")
        if type(secret_valid) == bool:
            error = "Incorrect Secret"
            error_list.append(error)
        else:
            hashed_secret = secret_valid

        if len(error_list) == 0:

            admin = AdminCreate(
                first_name=user_full_name_list[0],
                middle_name=user_full_name_list[1],
                last_name=user_full_name_list[2],
                gender=gender_bool,
                contact_number=form.contact_number,
                email=form.email,
                password=password,
                secret_for_administration=hashed_secret)
            try:
                admin = create_admin(admin=admin, db=db)
                return responses.RedirectResponse(
                    "/login/", status_code=status.HTTP_302_FOUND
                )  # default is post request, to use get request added status code 302
            except IntegrityError:
                form.__dict__.get("errors").append("Duplicate email")
                return templates.TemplateResponse("registration/admin_registration.html", form.__dict__)
        else:
            for error in error_list:
                form.__dict__.get("errors").append(error)
            return templates.TemplateResponse("registration/admin_registration.html", form.__dict__)

    return templates.TemplateResponse("registration/admin_registration.html", form.__dict__)
