from fastapi.security.utils import get_authorization_scheme_param
from fastapi import status, responses

from app.apis.version1.route_login import login_for_access_token, get_current_user_from_token, authenticate_user
from app.db.models import Admin
from app.db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.routers.auth.forms import LoginForm


templates = Jinja2Templates(directory="app/templates")
router = APIRouter(include_in_schema=False)


@router.get("/login/")
def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login/")
async def login(request: Request, db: Session = Depends(get_db)):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            user = authenticate_user(
                db=db,
                username=form.username,
                password=form.password
            )
            if user:
                # Determine the redirect URL based on user type
                redirect_url = {
                    "admin": "/admin/dashboard/",
                    "doctor": "/doctor/dashboard/",
                    "patient": "/patient/dashboard/"
                }.get(user.user_type, "/login/")
                
                # Create RedirectResponse and set cookie
                response = responses.RedirectResponse(
                    redirect_url, status_code=status.HTTP_302_FOUND
                )
                # Generate and set the access token cookie
                login_for_access_token(response=response, form_data=form, db=db)
                return response
            else:
                form.errors.append("Incorrect Email or Password, or Not Registered!")
                return templates.TemplateResponse("auth/login.html", form.__dict__)
        except HTTPException:
            form.errors.append("Incorrect Email or Password, or Not Registered!")
            return templates.TemplateResponse("auth/login.html", form.__dict__)
    return templates.TemplateResponse("auth/login.html", form.__dict__)