from typing import Optional

from fastapi import Body
from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime

from app.main.schemas import UserAuthentication, File, DataList, Address, AddressCreate, AddressUpdate
from app.main.schemas.user import AddedBy


class Nursery(BaseModel):
    uuid: str
    email: EmailStr
    name: str
    total_places: int = 0
    phone_number: str
    status: str
    logo: Optional[File]
    signature: Optional[File]
    stamp: Optional[File]
    address: Address
    owner: AddedBy
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)


class NurseryCreateBase(BaseModel):
    email: EmailStr
    name: str
    logo_uuid: Optional[str] = None
    signature_uuid: Optional[str] = None
    stamp_uuid: Optional[str] = None
    total_places: int = Body(0, ge=0)
    phone_number: str
    owner_uuid: str

    model_config = ConfigDict(from_attributes=True)


class NurseryCreate(NurseryCreateBase):
    address: AddressCreate

    model_config = ConfigDict(from_attributes=True)


class NurseryCreateSchema(NurseryCreateBase):
    address_uuid: str

    model_config = ConfigDict(from_attributes=True)


class NurseryUpdateBase(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    logo_uuid: Optional[str] = None
    signature_uuid: Optional[str] = None
    stamp_uuid: Optional[str] = None
    total_places: int = None
    phone_number: Optional[str] = None
    address: Optional[AddressUpdate]


class NurseryUpdate(NurseryUpdateBase):
    uuid: str


class NurseryDelete(BaseModel):
    uuid: list[str]


class NurseryList(DataList):
    data: list[Nursery]

    model_config = ConfigDict(from_attributes=True)
