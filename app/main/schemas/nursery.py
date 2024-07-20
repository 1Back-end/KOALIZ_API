from typing import Optional

from fastapi import Body
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, model_validator, root_validator
from datetime import datetime, time

from app.main.core.i18n import __
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
    from_time: str = Body(..., regex=r'^\d{2}:\d{2}$')
    to_time: str = Body(..., regex=r'^\d{2}:\d{2}$')

    @model_validator(mode='wrap')
    def validate_to_after_from(self, handler):
        validated_self = handler(self)
        from_time = validated_self.from_time
        to_time = validated_self.to_time
        try:
            from_time_obj = time.fromisoformat(from_time)
            to_time_obj = time.fromisoformat(to_time)
        except ValueError:
            raise ValueError(__("invalid-time-format"))
        if to_time_obj <= from_time_obj:
            raise ValueError(__("to-not-greater-from"))
        return validated_self


class OpeningHoursInput(BaseModel):
    """
    Model representing opening hours for a specific day.
    """
    day_of_week: int
    hours: Optional[TimeRangeInput]

    @field_validator("day_of_week")
    def validate_day_of_week(cls, value):
        if value < 0 or value > 6:
            raise ValueError("Invalid day of week. Must be between 0 (Sunday) and 6 (Saturday).")
        return value


class OpeningHours(BaseModel):
    day_of_week: int
    from_time: str
    to_time: str

    model_config = ConfigDict(from_attributes=True)


class OpeningHoursList(NurseryMini):
    opening_hours: list[OpeningHours]
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
    logo: Optional[File]
    address: Address
    others: list[OtherNurseryByGuest] = []

    model_config = ConfigDict(from_attributes=True)

