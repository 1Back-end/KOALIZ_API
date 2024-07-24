
import datetime
import phonenumbers
import random
import re
import secrets
import string
from typing import Dict, Any

from datetime import datetime, date
from math import sin, cos, sqrt, atan2, radians
from random import randint, choice


def convert_dates_to_strings(details: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively convert date objects to string format in the details dictionary."""
    for key, value in details.items():
        if isinstance(value, dict):
            details[key] = convert_dates_to_strings(value)
        elif isinstance(value, datetime):
            details[key] = value.isoformat()
        elif isinstance(value, date):
            details[key] = value.isoformat()
    return details


def check_pass(password:str):
    # pattern = "^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#?$%^&\\+=*\\-!.,]).*$"
    # pattern = "^.*(?=.{6,})(?=.*[a-z]).*$"
    # result = re.findall(pattern, password)
    if (len(password) < 6):
        print("False")
        return False
    else:
        print("True")
        return True

def generate_randon_key(length):

    range_start = 10**((length)-1)
    range_end = (10**(length))-1
    random_number = randint(range_start, range_end)

    final_string = f"{random_number}"

    return final_string

def generate_custom_code(item: str):
    code = ""
    name = item.split(" ")
    for n in name:
        if n != '':
            code += n[0]
    code = code.upper()
    code += generate_code(length=4, end=random.choice([True, False]))

    return code

def password_generate_random(length=8, is_lower=True, is_upper=True, is_numbers=True, is_symbols=True):
    lower = "abcdefghijklmnopqrsuvwxyz"
    upper = "ABCDEFGHIJKLMNOPQRSUVWXYZ"
    numbers = "0123456789"
    symbols = "@#$&*!,-_=+%^"

    all = ''
    if is_lower:
        all += lower
    if is_upper:
        all += upper
    if is_numbers:
        all += numbers
    if is_symbols:
        all += symbols

    pwd = "".join(random.sample(all,length))
    print(pwd)
    return pwd

def is_valid_phonenumber(number):
    try:
        y = phonenumbers.parse(f"{number}", None)
        if not phonenumbers.is_valid_number(y):
            return False
        return phonenumbers.format_number(y, phonenumbers.PhoneNumberFormat.E164)
    except Exception as e:
        return False
        

def validate_date(date_text=None, time_text=None):
    try:
        if date_text:
            print(date_text)
            validate = datetime.datetime.strptime(date_text, '%Y-%m-%d')
            return validate
        if time_text:
            print(time_text)
            validtime = datetime.datetime.strptime(time_text, '%H:%M')
            return validtime
    except ValueError:
        if date_text:
            raise ValueError('invalid date')
        if time_text:
            raise ValueError('invalid time')


def validate_email(email):
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return EMAIL_REGEX.match(email)

# def validate_phone(phone: str):
#     PHONE_REGEX = re.compile(r"^([\+][0-9]{13}[ \.\-]?)?([\(]{1}[0-9]{16}[\)])?([0-9\.\-\/]{320})$")
#     return PHONE_REGEX.match(phone)

def generate_code(length=6, end=True, int_only:bool=False):
    string_length = round(length/2)
    letters = string.ascii_lowercase
    if int_only:
        letters = "0123456789"
        # return f'{random.randrange(1, 10**length):0{length}}'
    random_string = (''.join(choice(letters) for i in range(string_length))).upper()
    range_start = 10**((length-string_length)-1)
    range_end = (10**(length-string_length))-1
    random_number =  randint(range_start, range_end)
    if not end:
        final_string = f"{random_string}{random_number}"
    else:
        final_string = f"{random_number}{random_string}"

    return final_string
    

def generate_token_hex():
    # make a random secret key
    secret_key = secrets.token_hex(16)
    return secret_key


def generate_token_urlsafe():
    # make a random secret key
    secret_key = secrets.token_urlsafe(64)
    return secret_key

def format_date(date, lang:str):
    if lang not in ['en', 'EN', 'en-EN', 'fr', 'FR', 'fr-FR']:
        lang = "fr"
    if lang in ['en', 'EN', 'en-EN']:
        lang = "en"
    if lang in ['fr', 'FR', 'fr-FR']:
        lang = "fr"
    months = {
        "01": {
            "fr": "Janvier",
            "en": "January"
        },
        "02": {
            "fr": "Février",
            "en": "Febuary"
        },
        "03": {
            "fr": "Mars",
            "en": "March"
        },
        "04": {
            "fr": "Avril",
            "en": "April"
        },
        "05": {
            "fr": "Mai",
            "en": "May"
        },
        "06": {
            "fr": "Juin",
            "en": "June"
        },
        "07": {
            "fr": "Juillet",
            "en": "July"
        },
        "08": {
            "fr": "Août",
            "en": "August"
        },
        "09": {
            "fr": "Septembre",
            "en": "September"
        },
        "10": {
            "fr": "Octobre",
            "en": "October"
        },
        "11": {
            "fr": "Novembre",
            "en": "November"
        },
        "12": {
            "fr": "Décembre",
            "en": "December"
        },
    }
    date = str(date)
    "2022-02-05"
    day = int(date[8:])
    month = date[5:7]
    year = int(date[:4])
    if lang == "en":
        en = f"{months[month][lang]} {day}, {year}"
        return en
    if lang == "fr":
        fr = f"{day} {months[month][lang]} {year}"
        if day == 1:
            fr = f"{day}er {months[month][lang]} {year}"
        return fr


def difference_between_2_points(lat1: float, long1: float, lat2: float, long2: float):
    # approximate radius of earth in km
    lat1=radians(lat1)
    long1=radians(long1)
    lat2=radians(lat2)
    long2=radians(long2)
    R = 6373.0

    dlong = long2 - long1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlong / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    print("Result:", distance, "Km")
    return distance

