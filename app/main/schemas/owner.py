from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime

from app.main.schemas import UserAuthentication, File, DataList
from app.main.schemas.user import AddedBy


class Owner(BaseModel):
    uuid: Optional[str] = None
    email: EmailStr
    firstname: Optional[str]
    lastname: str
    status: str
    phone_number: Optional[str]
    is_new_user: Optional[bool] = False
    avatar: Optional[File]
    added_by: Optional[AddedBy]
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)


class OwnerSchemaBase(BaseModel):
    firstname: Optional[str] = None
    lastname: str
    avatar_uuid: Optional[str] = None
    phone_number: Optional[str] = None


class OwnerCreate(OwnerSchemaBase):
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class OwnerUpdateBase(OwnerSchemaBase):
    pass


class OwnerUpdate(OwnerUpdateBase):
    uuid: str


class OwnerDelete(BaseModel):
    uuid: list[str]


class OwnerList(DataList):
    data: list[Owner]

    model_config = ConfigDict(from_attributes=True)


class OwnerAuthentication(UserAuthentication):
    user: Owner

    model_config = ConfigDict(from_attributes=True)
