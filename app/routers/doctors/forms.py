from datetime import datetime
from datetime import date
from typing import List
from typing import Optional

from fastapi import Request


class DoctorCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.first_name: Optional[str] = None
        self.middle_name: Optional[str] = None
        self.last_name: Optional[str] = None
        self.secret_for_doctor: Optional[str] = None
        self.email: Optional[str] = None
        self.password: Optional[str] = None
        self.specialization_name: Optional[str] = None
        self.professional_statement: Optional[str] = None
        self.practicing_from: Optional[date] = None
        self.qualification_name_list: list[str] = []
        self.institute_name_list: list[str] = []
        self.procurement_year_list: list[int] = []
        self.hospital_name_list: list[str] = []
        self.city_list: list[str] = []
        self.country_list: list[str] = []
        self.start_date_list: list[date] = []
        self.end_date_list: list[date] = []

    async def load_data(self):
        form = await self.request.form()
        self.first_name = form.get("first_name")
        self.middle_name = form.get("middle_name")
        self.last_name = form.get("last_name")
        self.email = form.get("email")
        self.secret_for_doctor = form.get("secret_for_doctor")
        self.password = form.get("password")
        self.specialization_name = form.get("specialization_name")
        self.professional_statement = form.get("professional_statement")
        self.practicing_from = form.get("practicing_from")
        i = int(form.get('i'))
        print(i)
        for i in range(0, i):
            print(i)
            qualification_name = form.get(f'qualification_name[{i}]')
            self.qualification_name_list.append(qualification_name)
            institute_name = form.get(f'institute_name[{i}]')
            self.institute_name_list.append(institute_name)
            procurement_year = form.get(f'procurement_year[{i}]')
            self.procurement_year_list.append(procurement_year)

        j = int(form.get('j'))
        print(j)
        for j in range(0, j):
            hospital_name = form.get(f'hospital_name[{j}]')
            self.hospital_name_list.append(hospital_name)
            city = form.get(f'city[{j}]')
            self.city_list.append(city)
            country = form.get(f'country[{j}]')
            self.country_list.append(country)
            start_date = form.get(f'start_date[{j}]')
            self.start_date_list.append(start_date)
            end_date = form.get(f'end_date[{j}]')
            self.end_date_list.append(end_date)

    async def is_valid(self):
        if not self.email or not (self.email.__contains__("@")):
            self.errors.append("Email is required")
        if not self.password or not len(self.password) >= 4:
            self.errors.append("Password must be > 4 chars")
        if not self.errors:
            return True
        return False
