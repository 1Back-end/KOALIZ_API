from typing import Optional, Any

from fastapi import Body, HTTPException, Query
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, model_validator
from datetime import datetime, time, date

from app.main import models
from app.main.core.i18n import __
from app.main.schemas import DataList, NurseryMini
from app.main.schemas.base import Items


@field_validator("birthdate")
class ChildSchema(BaseModel):
    firstname: str
    lastname: str
    gender: models.Gender
    birthdate: date
    birthplace: str

    @field_validator("birthdate")
    def validate_birthdate(cls, value):
        if value >= date.today():
            raise ValueError("Birthdate must be before today's date.")
        return value

@field_validator("birthdate")
class ChildUpdateSchema(BaseModel):
    uuid: str
    firstname: str
    lastname: str
    gender: models.Gender
    birthdate: date
    birthplace: str

    @field_validator("birthdate")
    def validate_birthdate(cls, value):
        if value >= date.today():
            raise ValueError("Birthdate must be before today's date.")
        return value


class TimeSlotInputSchema(BaseModel):
    """
    Model representing a time range (from_time, to_time).
    """
    from_time: str = Body(..., regex=r'^\d{2}:\d{2}$')
    to_time: str = Body(..., regex=r'^\d{2}:\d{2}$')

    @model_validator(mode='wrap')
    def validate_to_after_from(self, handler):
        validated_self = handler(self)
        try:
            from_time_obj = time.fromisoformat(validated_self.from_time)
            to_time_obj = time.fromisoformat(validated_self.to_time)
        except ValueError:
            raise ValueError(__("invalid-time-format"))

        if to_time_obj <= from_time_obj:
            raise ValueError('to_time must be after from_time')
        return validated_self

    model_config = ConfigDict(from_attributes=True)


class PreContractSchema(BaseModel):
    begin_date: date
    end_date: date
    typical_weeks: list[list[list[TimeSlotInputSchema]]]

    @model_validator(mode='wrap')
    def validate_end_date(self, handler):
        validated_self = handler(self)
        for week in validated_self.typical_weeks:
            for day in week:
                if len(day) > 5:
                    raise HTTPException(status_code=422, detail=("Each week's data list cannot exceed 5 items"))

        begin_date = validated_self.begin_date
        if validated_self.end_date <= begin_date:
            raise ValueError("End date must be after to begin date.")
        return validated_self


class PreContractUpdateSchema(BaseModel):
    uuid: str
    begin_date: date
    end_date: date
    typical_weeks: list[list[list[TimeSlotInputSchema]]]

    @field_validator('typical_weeks')
    def validate_week_length(cls, value):
        for week in value:
            if len(week) > 5:
                raise HTTPException(status_code=422, detail=("Each week's data list cannot exceed 5 items"))
        return value

    @field_validator("end_date")
    def validate_end_date(cls, value, values):
        begin_date = values.data.get('begin_date')
        if value <= begin_date:
            raise ValueError("End date must be after to begin date.")
        return value

class ParentGuestSchema(BaseModel):
    link: models.ParentRelationship
    firstname: str
    lastname: str
    birthplace: str
    fix_phone: str = None
    phone: str
    email: EmailStr
    recipient_number: str
    zip_code: str
    city: str
    country: str
    profession: str
    annual_income: float
    company_name: str
    has_company_contract: bool
    dependent_children: int
    disabled_children: int


class PreregistrationCreate(BaseModel):
    child: ChildSchema
    nurseries: list[str]
    pre_contract: PreContractSchema
    parents: list[ParentGuestSchema]
    note: str = None

    model_config = ConfigDict(from_attributes=True)


class PreContract(BaseModel):
    begin_date: date
    end_date: date
    typical_weeks: list[Any]

    model_config = ConfigDict(from_attributes=True)


class ParentGuest(BaseModel):
    link: models.ParentRelationship
    firstname: str
    lastname: str
    fix_phone: str = None
    phone: str
    email: EmailStr
    zip_code: str
    city: str
    country: str
    profession: str

    model_config = ConfigDict(from_attributes=True)


class PreregistrationMini(BaseModel):
    uuid: str
    nursery: NurseryMini
    note: str = None
    status: str = None

    model_config = ConfigDict(from_attributes=True)


class ChildDetails(BaseModel):
    uuid: str
    firstname: str
    lastname: str
    gender: models.Gender
    birthdate: date
    birthplace: str
    date_added: datetime
    date_modified: datetime
    parents: list[ParentGuest]
    pre_contract: PreContract
    preregistrations: list[PreregistrationMini]
    model_config = ConfigDict(from_attributes=True)

class ParentDisplay(BaseModel):
    uuid: str= None
    link: models.ParentRelationship= None
    firstname: str= None
    lastname: str= None
    birthplace: str= None
    fix_phone: str = None
    phone: str= None
    email: EmailStr= None
    recipient_number: str= None
    zip_code: str= None
    city: str= None
    country: str= None
    profession: str= None
    annual_income: float= None
    company_name: str= None
    has_company_contract: bool= None
    dependent_children: int= None
    disabled_children: int= None

    model_config = ConfigDict(from_attributes=True)
class ChildMini(BaseModel):
    uuid: str
    firstname: str
    lastname: str
    gender: models.Gender
    birthdate: date
    birthplace: str
    date_added: datetime
    date_modified: datetime
    parents: list[ParentDisplay]
    model_config = ConfigDict(from_attributes=True)


    model_config = ConfigDict(from_attributes=True)
class TrackingCaseMini(BaseModel):
    uuid: str
    details: Any
    interaction_type: str
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class PreregistrationDetails(BaseModel):
    uuid: str
    code: str
    child: ChildMini
    nursery: NurseryMini
    pre_contract: PreContract
    tracking_cases: list[TrackingCaseMini]
    note: str = None
    status: str = None
    accepted_date: Optional[datetime] = None
    refused_date: Optional[datetime] = None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)


class PreregistrationUpdate(BaseModel):
    uuid: str
    child: ChildUpdateSchema
    nurseries: list[str]
    pre_contract: PreContractUpdateSchema
    parents: list[ParentGuestSchema]
    note: str = None

    model_config = ConfigDict(from_attributes=True)

class TrackingCase(BaseModel):
    preregistration_uuid: str
    details: Items

    model_config = ConfigDict(from_attributes=True)

class ActivityReminder(BaseModel):
    preregistration_uuid: str
    title: str
    activity_reminder_type_uuid: str
    datetime:datetime
    description:Optional[str]= None

class MeetingType(BaseModel):
    preregistration_uuid: str
    meeting_type_uuid: str
    meeting_date:date
    meeting_time: str = Body(..., regex=r'^\d{2}:\d{2}$')
    description:Optional[str]= None


    # model_config = ConfigDict(from_attributes=True)

class ChildSlim(BaseModel):
    uuid: str
    firstname: str
    lastname: str
    gender: models.Gender
    birthdate: date

    model_config = ConfigDict(from_attributes=True)


class PreContractSlim(BaseModel):
    begin_date: date
    end_date: date

    model_config = ConfigDict(from_attributes=True)


class PreregistrationSlim(BaseModel):
    uuid: str
    child: ChildSlim
    pre_contract: PreContractSlim
    status: str = None

    model_config = ConfigDict(from_attributes=True)

class PreRegistrationList(DataList):
    data: list[PreregistrationSlim] = []

    model_config = ConfigDict(from_attributes=True)
class TrackingCaseList(DataList):
    data: list[TrackingCaseMini]

    model_config = ConfigDict(from_attributes=True)


class TransferPreRegistration(BaseModel):
    nursery_uuid: str

