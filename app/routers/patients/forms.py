from datetime import date
from typing import List
from typing import Optional

from fastapi import Request


class PatientCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.first_name: Optional[str] = None
        self.middle_name: Optional[str] = None
        self.last_name: Optional[str] = None
        self.contact_number: Optional[str] = None
        self.date_of_birth: Optional[str] = None
        self.weight: Optional[int] = None
        self.length: Optional[int] = None
        self.gender: Optional[bool] = None
        self.medicines: Optional[str] = None
        self.pathological_cases: Optional[str] = None
        self.permanent_health_symptoms: Optional[str] = None
        self.surgeries: Optional[str] = None
        self.email: Optional[str] = None
        self.password: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.first_name = form.get("first_name")
        self.middle_name = form.get("middle_name")
        self.last_name = form.get("last_name")
        self.contact_number = form.get("contact_number")
        self.date_of_birth = form.get("date_of_birth")
        print(type(self.date_of_birth))
        self.weight = form.get("weight")
        self.length = form.get("length")
        self.gender = form.get("gender")
        self.medicines = form.get("medicines")
        self.pathological_cases = form.get("pathological_cases")
        self.permanent_health_symptoms = form.get("permanent_health_symptoms")
        self.surgeries = form.get("surgeries")
        self.email = form.get("email")
        self.password = form.get("password")

    async def is_valid(self):
        if not self.email or not (self.email.__contains__("@")):
            self.errors.append("Email is required")
        if not self.password or not len(self.password) >= 4:
            self.errors.append("Password must be > 4 chars")
        if not self.errors:
            return True
        return False


class PatientEditForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.first_name: Optional[str] = None
        self.middle_name: Optional[str] = None
        self.last_name: Optional[str] = None
        self.contact_number: Optional[str] = None
        self.date_of_birth: Optional[str] = None
        self.weight: Optional[int] = None
        self.length: Optional[int] = None
        self.gender: Optional[bool] = None
        self.medicines: Optional[str] = None
        self.pathological_cases: Optional[str] = None
        self.permanent_health_symptoms: Optional[str] = None
        self.surgeries: Optional[str] = None
        self.email: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.first_name = form.get("first_name")
        self.middle_name = form.get("middle_name")
        self.last_name = form.get("last_name")
        self.contact_number = form.get("contact_number")
        self.date_of_birth = form.get("date_of_birth")
        print(type(self.date_of_birth))
        self.weight = form.get("weight")
        self.length = form.get("length")
        self.gender = form.get("gender")
        self.medicines = form.get("medicines")
        self.pathological_cases = form.get("pathological_cases")
        self.permanent_health_symptoms = form.get("permanent_health_symptoms")
        self.surgeries = form.get("surgeries")
        self.email = form.get("email")

    async def is_valid(self):
        if not self.email or not (self.email.__contains__("@")):
            self.errors.append("Email is required")
        if not self.errors:
            return True
        return False


class SpecializationChooseForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.specialization_name: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.specialization_name = form.get("specialization_name")

    async def is_valid(self):
        if not self.specialization_name:
            self.errors.append("Specialization name is required")
        return not self.errors  # Return True if errors is empty, False otherwise


class PatientLocationForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.patient_latitude: Optional[float] = None
        self.patient_longitude: Optional[float] = None

    async def load_data(self):
        form = await self.request.form()

        self.patient_latitude = float(form.get("patient_latitude"))
        self.patient_longitude = float(form.get("patient_latitude"))

    async def is_valid(self):
        if not self.errors:
            return True
        return False
