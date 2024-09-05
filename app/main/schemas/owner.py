from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime

from app.main.schemas import UserAuthentication, File, DataList
from app.main.schemas.user import AddedBy
from app .main.schemas.nursery import Nursery, NurserySlim1


class NurseryMiniSlim(BaseModel):
    uuid: str
    name: str

    model_config = ConfigDict(from_attributes=True)


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


class OwnerWithNursery(BaseModel):
    uuid: Optional[str] = None
    email: EmailStr
    firstname: Optional[str]
    lastname: str
    status: str
    valid_nurseries:list[NurserySlim1] =[]
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
    user: OwnerWithNursery

    model_config = ConfigDict(from_attributes=True)


class AssistantCreate(OwnerCreate):
    nursery_uuids: list[str]

    model_config = ConfigDict(from_attributes=True)


class AssistantUpdate(OwnerUpdateBase):
    nursery_uuids: list[str]

    model_config = ConfigDict(from_attributes=True)


class AssistantDelete(OwnerDelete):
    pass


class Assistant(Owner):
    structures: list[NurserySlim1] = Field([], serialization_alias="nurseries")

    model_config = ConfigDict(from_attributes=True)


class AssistantList(DataList):
    data: list[Owner]

    model_config = ConfigDict(from_attributes=True)
