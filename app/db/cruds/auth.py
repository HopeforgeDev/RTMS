from datetime import date, datetime

from app.core.hashing import Hasher

import re


def validate_date(start_datetime: datetime or None,
                  end_datetime: datetime | None,
                  past_date: date | None,
                  start_date: date | None,
                  end_date: date | None,
):

    print(past_date)

    invalid = False

    if start_date is not None and end_date is not None and start_date > end_date:
        invalid = True

    elif start_datetime is not None and end_datetime is not None and start_datetime > end_datetime:
        invalid = True

    elif past_date is not None and past_date > date.today():
        invalid = True

    elif end_datetime is not None and end_datetime < datetime.utcnow():
        invalid = True

    return invalid


def validate_secret(
        secret_to_validate: str,
        secret: str):
    valid = False
    real_hashed_secret = Hasher.get_password_hash(secret)

    if Hasher.verify_password(secret_to_validate, real_hashed_secret):
        valid = True
        secret_to_validate = real_hashed_secret
        print(secret_to_validate)
        return secret_to_validate

    if not valid:
        return valid


def validate_email(
    email: str,
    user_type: str,
    pat: str):

    validated = False
    pat_concat = "^[a-z0-9]+"
    patted = pat_concat + pat + "$"
    if user_type == "doctor":
        if re.match(patted, email):
            validated = True
    elif user_type == "patient":
        if re.match(patted, email):
            validated = True
    elif user_type == "admin":
        if re.match(patted, email):
            validated = True

    return validated


def validate_full_name(
    first_name: str,
    middle_name: str,
    last_name: str,
    ):

    user_first_name = first_name.lower().capitalize()

    user_middle_name = middle_name.lower().capitalize()

    user_last_name = last_name.lower().capitalize()

    user_full_name = [user_first_name, user_middle_name, user_last_name]

    return user_full_name
