from typing import List
from typing import Optional

from app.apis.version1.route_login import get_current_user_from_token
from app.db.models.doctor_models import Doctor
from app.db.models.admin_models import Admin
from app.db.cruds.doctor import create_doctor
from app.db.cruds.doctor import get_doctors
from app.db.cruds.doctor import get_doctor
from app.db.cruds.doctor import update_doctor_by_id
from app.db.cruds.doctor import delete_doctor_by_id
from app.db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.templating import Jinja2Templates
from app.schemas import schemas
from app.schemas.schemas import Doctor
from sqlalchemy.orm import Session
from app.db.cruds.doctor import search_for_doctor_id_by_doctor_full_name


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.post("/create-doctor/", response_model=Doctor)
def create__doctor(
    doctor: schemas.DoctorCreate,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user_from_token),
):
    if current_user:
        doctor = create_doctor(doctor=doctor, db=db)
        return doctor


@router.get(
    "/get/{id}", response_model=schemas.Doctor
)  # if we keep just "{id}" . it would stat catching all routes
def read_job(doctor_id: int, db: Session = Depends(get_db)):
    doctor = get_doctor(doctor_id=doctor_id, db=db)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with this id {id} does not exist",
        )
    return doctor


@router.get("/all", response_model=List[schemas.Doctor])
def read_jobs(db: Session = Depends(get_db)):
    doctors = get_doctors(db=db)
    return doctors


@router.put("/update/{id}")
def update_job(doctor_id: int, doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    current_user = 1
    message = update_doctor_by_id(doctor_id=doctor_id, doctor=doctor, db=db)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with id {id} not found"
        )
    return {"msg": "Successfully updated data."}


@router.delete("/delete/{id}")
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user_from_token),
):
    doctor = get_doctor(doctor_id=doctor_id, db=db)
    if not doctor:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with id {id} does not exist",
        )
    if current_user.user_type == "admin":
        delete_doctor_by_id(doctor_id=doctor_id, db=db)
        return {"detail": "Successfully deleted."}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not permitted!!!!"
    )


# @router.get("/autocomplete")
# def autocomplete(term: Optional[str] = None, db: Session = Depends(get_db)):
#
