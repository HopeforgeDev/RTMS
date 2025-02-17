from datetime import time, datetime
from datetime import date
from typing import List
from typing import Optional

from fastapi import Request


class AppointmentCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.probable_start_time: Optional[time] = None
        self.actual_end_time: Optional[time] = None
        self.appointment_taken_date: Optional[date] = None

    async def load_data(self):
        form = await self.request.form()

        appointment_taken_datetime = str(form.get("appointment_taken_datetime")).split(" | ")
        self.appointment_taken_date = datetime.strptime(appointment_taken_datetime[0], '%Y-%m-%d').date()
        self.probable_start_time = datetime.strptime(appointment_taken_datetime[1], '%H:%M:%S').time()
        self.actual_end_time = datetime.strptime(appointment_taken_datetime[2], '%H:%M:%S').time()

    async def is_valid(self):
        if not self.errors:
            return True
        return False
