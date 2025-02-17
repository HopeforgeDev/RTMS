from app.schemas import schemas
from sqlalchemy.orm import Session

from fastapi import Depends

from app.db.session import get_db

from app.db.models import admin_models

from app.core import hashing

from app.db.cruds import auth

from app.schemas.schemas import AdminCreate


def get_admin_by_email(db: Session, email: str):
    admin = db.query(admin_models.Admin).filter(admin_models.Admin.email == email).first()

    return admin


def get_admins(db: Session, skip: int = 0, limit: int = 100):
    admins = db.query(admin_models.Admin).offset(skip).limit(limit).all()
    return admins


def create_admin(
        admin: AdminCreate,
        db: Session = Depends(get_db)):

    new_admin = admin_models.Admin(
        first_name=admin.first_name,
        middle_name=admin.middle_name,
        last_name=admin.last_name,
        gender=admin.gender,
        contact_number=admin.contact_number,
        email=admin.email,
        password=admin.password,
        secret_for_administration=admin.secret_for_administration)

    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return new_admin


def update_admin_by_id(admin_id: int, admin: schemas.AdminCreate, db: Session):
    existing_admin = db.query(admin_models.Admin).filter(admin_models.Admin.id == admin_id)
    if not existing_admin.first():
        return 0
    admin.__dict__.update(
        id=admin_id
    )  # update dictionary with new key value of owner_id
    existing_admin.update(admin.__dict__)
    db.commit()
    return 1
