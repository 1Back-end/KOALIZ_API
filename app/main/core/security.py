import re
import string
import random
import jwt
import bcrypt
from datetime import timedelta, datetime
from random import randint, choice
from typing import Union, Any
from fastapi import HTTPException, status
from .config import Config
from app.main.core.i18n import __

ALGORITHM = "HS256"


def validate_email(email):
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return email_regex.match(email)


def generate_code(length=6, end=True):
    """Generate a random string of fixed length """
    string_length = round(length / 2)
    letters = string.ascii_lowercase
    random_string = (''.join(choice(letters) for i in range(string_length))).upper()
    range_start = 10 ** ((length - string_length) - 1)
    range_end = (10 ** (length - string_length)) - 1
    random_number = randint(range_start, range_end)
    if not end:
        final_string = f"{random_string}{random_number}"
    else:
        final_string = f"{random_number}{random_string}"

    return final_string


def create_access_token(
        subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, Config.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        decoded_token = jwt.decode(token, Config.SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token
    except Exception as e:
        if token:
            print("Failed to decode token")
            print(token)
            print(e)
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()

    # Hashing the password
    return (bcrypt.hashpw(password.encode('utf-8'), salt)).decode('utf-8')


def check_pass(password: str):
    # 8 characters length and 1 special character
    pattern = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
    result = re.findall(pattern, password)
    if (len(password) < 8) or not result:
        print("False")
        return False
    else:
        print("True")
        return True


def is_apikey(api_key: str):
    if api_key != Config.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=__("bad-api-key")
        )
