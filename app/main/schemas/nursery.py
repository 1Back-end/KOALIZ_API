from typing import Optional

from fastapi import Body
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from datetime import datetime, time

from app.main.schemas import UserAuthentication, File, DataList, Address, AddressCreate, AddressUpdate
from app.main.schemas.user import AddedBy


class NurseryMini(BaseModel):
    uuid: str
    email: EmailStr
    name: str
    total_places: int = 0
    phone_number: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class Nursery(BaseModel):
    uuid: str
    email: EmailStr
    name: str
    total_places: int = 0
    phone_number: str
    status: str
    open_from: Optional[str]
    open_to: Optional[str]
    website: Optional[str] = None
    slug: Optional[str] = None
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
    website: Optional[str] = None
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
    website: Optional[str]
    address: Optional[AddressUpdate]


class NurseryUpdate(NurseryUpdateBase):
    uuid: str


class NurseryDelete(BaseModel):
    uuid: list[str]


class NurseryList(DataList):
    data: list[Nursery]

    model_config = ConfigDict(from_attributes=True)


class TimeRangeInput(BaseModel):
    """
    Model representing a time range (from_time, to_time).
    """
    from_time: str = Body(..., pattern="00:00")
    to_time: str = Body(..., pattern="00:00")

    @field_validator("from_time", "to_time")
    def validate_time_format(cls, value):
        try:
            time.fromisoformat(value)
            return value
        except ValueError:
            raise ValueError("Invalid time format. Use ISO format (HH:MM).")


class OpeningHoursInput(BaseModel):
    """
    Model representing opening hours for a specific day.
    """
    day_of_week: int
    hours: Optional[TimeRangeInput]

    @field_validator("day_of_week")
    def validate_day_of_week(cls, value):
        if not 0 <= value <= 6:
            raise ValueError("Invalid day of week. Must be between 0 (Sunday) and 6 (Saturday).")


class TimeRange(BaseModel):
    from_time: str
    to_time: str

    model_config = ConfigDict(from_attributes=True)


class OpeningHours(BaseModel):
    day_of_week: int
    hours: Optional[TimeRange] = None

    model_config = ConfigDict(from_attributes=True)

class OpeningHoursList(BaseModel):
    nursery: NurseryMini
    opening_hours: list[OpeningHours]
    model_config = ConfigDict(from_attributes=True)


class OpeningTime(BaseModel):
    """
    Model representing a time range (from_time, to_time).
    """
    # open_from: str = Body(..., pattern="00:00")
    open_from: str = Body(...)
    open_to: str = Body(...)

    @field_validator("open_from", "open_to")
    def validate_time_format(cls, value):
        try:
            time.fromisoformat(value)
            return value
        except ValueError:
            raise ValueError("Invalid time format. Use ISO format (HH:MM).")


class NurseryOpeningTime(BaseModel):
    uuid: str
    name: str
    status: str
    open_from: str
    open_to: str

    model_config = ConfigDict(from_attributes=True)


class OtherNurseryByGuest(BaseModel):
    uuid: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class NurseryByGuest(BaseModel):
    uuid: str
    email: EmailStr
    name: str
    phone_number: str
    open_from: Optional[str]
    open_to: Optional[str]
    logo: Optional[File]
    address: Address
    others: list[OtherNurseryByGuest] = []

    model_config = ConfigDict(from_attributes=True)

