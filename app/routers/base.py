from fastapi import APIRouter
from app.routers.auth import login
from app.routers.admins import admin
from app.routers.admins import admin_sign_up
from app.routers.doctors import doctor
from app.routers.doctors import doctor_sign_up
from app.routers.patients import patient
from app.routers.patients import patient_sign_up

router = APIRouter()
router.include_router(login.router, prefix="", tags=["auth-webapp"])
router.include_router(admin.router, prefix="", tags=["admin-webapp"])
router.include_router(admin_sign_up.router, prefix="", tags=["admin_sign_up-webapp"])
router.include_router(doctor.router, prefix="", tags=["doctor-webapp"])
router.include_router(doctor_sign_up.router, prefix="", tags=["doctor_sign_up-webapp"])
router.include_router(patient.router, prefix="", tags=["patient-webapp"])
router.include_router(patient_sign_up.router, prefix="", tags=["patient_sign_up-webapp"])
