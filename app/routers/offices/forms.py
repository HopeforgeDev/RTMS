from datetime import time
from datetime import date
from typing import List
from typing import Optional

from fastapi import Request


class OfficeCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.time_slot_per_client_in_min: Optional[int] = None
        self.hospital_affiliation_option: Optional[int] = None
        self.first_consultation_fee: Optional[int] = None
        self.followup_consultation_fee: Optional[int] = None
        self.city: Optional[str] = None
        self.country: Optional[str] = None
        self.date_list: Optional[list[date]] = []
        self.start_time_list: Optional[list[time]] = []
        self.end_time_list: Optional[list[time]] = []
        self.reason_of_unavailability_list: Optional[list[str]] = []
        self.insurance_name_list: Optional[list[str]] = []
        self.office_latitude: Optional[float] = None
        self.office_longitude: Optional[float] = None

    async def load_data(self):
        form = await self.request.form()
        self.hospital_affiliation_option = form.get("hospital_affiliation_option")
        self.time_slot_per_client_in_min = form.get("time_slot_per_client_in_min")
        self.first_consultation_fee = form.get("first_consultation_fee")
        self.followup_consultation_fee = form.get("followup_consultation_fee")
        self.city = form.get("city")
        self.country = form.get("country")
        i = int(form.get('i'))
        for i in range(0, i):
            date = form.get(f"date[{i}]")
            self.date_list.append(date)
            start_time = form.get(f"start_time[{i}]")
            self.start_time_list.append(start_time)
            end_time = form.get(f"end_time[{i}]")
            self.end_time_list.append(end_time)
            reason_of_unavailability = form.get(f"reason_of_unavailability[{i}]")
            if not reason_of_unavailability:
                reason_of_unavailability = "available"
            self.reason_of_unavailability_list.append(reason_of_unavailability)
        j = int(form.get('j'))
        for j in range(0, j):
            insurance_name = form.get(f'insurance_name[{j}]')
            print(insurance_name)
            self.insurance_name_list.append(insurance_name)

    async def is_valid(self):
        if not self.errors:
            return True
        return False
