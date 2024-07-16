from datetime import datetime, date
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict, EmailStr, Json

from app.main.schemas import DataList
from app.main.schemas.role import RoleBase


class AddedBy(BaseModel):
    uuid: str
    email: EmailStr
    firstname: Optional[str]
    lastname: str

    model_config = ConfigDict(from_attributes=True)

class Login(BaseModel):
    email: EmailStr
    password: str


class ResetPasswordStep1(BaseModel):
    email: EmailStr
    new_password: str


class ResetPasswordStep2(BaseModel):
    email: EmailStr
    otp: str


class UserBase(BaseModel):
    email: EmailStr
    firstname: str
    lastname: str

    model_config = ConfigDict(from_attributes=True)


class User(UserBase):
    uuid: Optional[str] = None
    date_added: datetime
    date_modified: datetime


class Storage(BaseModel):
    uuid: Optional[str] = None
    file_name: Optional[str] = None
    url: Optional[str] = None
    mimetype: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    size: Optional[int] = None
    thumbnail: Any = None
    medium: Any = None
    date_added: Optional[datetime] = None
    date_modified: Optional[datetime] = None


class UserProfileResponse(UserBase):
    uuid: Optional[str] = None
    role: RoleBase
    date_added: datetime
    date_modified: datetime
    avatar: Optional[Storage] = None



class UserDetail(User):
    uuid: str
    avatar: Optional[Storage] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    pass


class UserList(DataList):
    data: List[User] = []


class UserUpdate(BaseModel):
    user_uuid: str
    country_code: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    birthday: Optional[date] = None
    storage_uuid: str = None
