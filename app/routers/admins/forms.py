from typing import List
from typing import Optional

from fastapi import Request


class AdminCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.first_name: Optional[str] = None
        self.middle_name: Optional[str] = None
        self.last_name: Optional[str] = None
        self.contact_number: Optional[str] = None
        self.gender: Optional[bool] = None
        self.secret_for_administration: Optional[str] = None
        self.email: Optional[str] = None
        self.password: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.first_name = form.get("first_name")
        self.middle_name = form.get("middle_name")
        self.last_name = form.get("last_name")
        self.contact_number = form.get("contact_number")
        self.gender = form.get("gender")
        self.secret_for_administration = form.get("secret_for_administration")
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


class SpecializationCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.specialization_name: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.specialization_name = form.get("specialization_name")

    async def is_valid(self):
        if not self.errors:
            return True
        return False
