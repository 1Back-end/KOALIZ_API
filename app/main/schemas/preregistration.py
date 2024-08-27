from typing import Optional, Any, Text

from fastapi import Body, HTTPException, Query
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, model_validator
from datetime import datetime, time, date

from app.main import models
from app.main.core.i18n import __
from app.main.models.children import AdditionalCare, CareType, Cleanliness, MealQuality, MealTypeEnum, NapQuality, Route, StoolType
from app.main.schemas import DataList, NurseryMini
# from app.main.schemas.activity import ActivityResponse
from app.main.schemas.attendance import AttendanceMini
from app.main.schemas.base import Items
from app.main.schemas.user import  Storage
from app.main.schemas.file import File
from app.main.schemas import AddressSLim


@field_validator("birthdate")
class ChildSchema(BaseModel):
    firstname: str
    lastname: str
    gender: models.Gender
    birthdate: date
    birthplace: str

    # @field_validator("birthdate")
    # def validate_birthdate(cls, value):
    #     if value >= date.today():
    #         raise ValueError("Birthdate must be before today's date.")
    #     return value

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

class Tag(BaseModel):
    uuid: str
    title_fr: str
    title_en: str
    icon: Optional[Storage] = None
    description: Optional[str] = None
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


class PayingParentGuest(BaseModel):
    uuid: str
    annual_income: float = 0

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


class ChildResponse(BaseModel):
    uuid: str
    firstname: str
    lastname: str
    gender: models.Gender
    age : int
    nb_parent: int
    attendances: list[AttendanceMini]
    date_added: datetime
    model_config = ConfigDict(from_attributes=True)



class ChildMini2(BaseModel):
    uuid: str
    firstname: str
    lastname: str
    gender: models.Gender
    birthdate: date
    birthplace: str
    date_added: datetime
    date_modified: datetime
    paying_parent: Optional[PayingParentGuest] = None
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
    tags:Optional[list[Tag]] = []
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
    meeting_begin_time:str = Body(..., regex=r'^\d{2}:\d{2}$')
    meeting_end_time: str = Body(..., regex=r'^\d{2}:\d{2}$')
    meeting_time: str = Body(..., regex=r'^\d{2}:\d{2}$')
    description:Optional[str]= None


    # model_config = ConfigDict(from_attributes=True)

class MeetingTypeResponse(BaseModel):
    uuid: str
    title_en:  str
    title_fr:str
    model_config = ConfigDict(from_attributes=True)


class ActivityReminderTypeResponse(BaseModel):
    uuid: str
    title_en:  str
    title_fr:str
    model_config = ConfigDict(from_attributes=True)


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


class Icon(Storage):
    pass

class Tag(BaseModel):
    uuid: str
    title_fr: str
    title_en: str
    icon: Optional[Storage] = None
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class PreregistrationSlim(BaseModel):
    uuid: str
    child: ChildMini2
    pre_contract: PreContractSlim
    status: str = None
    tags: Optional[list[Tag]] = []

    model_config = ConfigDict(from_attributes=True)


class PreRegistrationList(DataList):
    data: list[PreregistrationSlim] = []

    model_config = ConfigDict(from_attributes=True)


class TrackingCaseList(DataList):
    data: list[TrackingCaseMini]

    model_config = ConfigDict(from_attributes=True)


class TransferPreRegistration(BaseModel):
    nursery_uuid: str

class NapSlim(BaseModel):
    uuid: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    quality: Optional[NapQuality] = None
    observation: Optional[str] = None
    duration: Optional[int] = 0
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class MealSlim(BaseModel):
    uuid: str
    # child: Optional[ChildMini2] = None
    meal_time: Optional[datetime] = None
    bottle_milk_ml: Optional[int] = None
    # breastfeeding_duration_minutes: Optional[int] = None
    meal_quality: Optional[MealQuality] = None
    meal_type:Optional[MealTypeEnum] = None
    product:Optional[Text] = None
    observation: Optional[str] = None    
    # nursery: Optional[NurserySlim]=None
    # added_by: Optional[EmployeBase]=None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class ActivitySlim(BaseModel):
    added_by_uuid: str
    # added_by:AddedBy
    nursery_uuid: str
    # nursery:NurseryMini
    child_uuid: str
    # child: ChildMini2
    activity_uuid: str
    # activity:ActivityResponse
    activity_time: datetime
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class HealthRecordSlim(BaseModel):
    uuid: Optional[str] = None
    medication_name: Optional[str]
    observation: Optional[str]
    medication_type: Optional[str]= None
    care_type: Optional[CareType]= None
    route: Optional[Route]= None
    time: Optional[datetime]= None
    weight: Optional[float] = 0
    temperature: Optional[float] = 0
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)


class HygieneChangeSlim(BaseModel):
    uuid: Optional[str] = None
    time: Optional[datetime]= None
    cleanliness: Optional[Cleanliness]= None
    pipi: Optional[bool] = False
    stool_type: Optional[StoolType]= None
    product:Optional[str] = None
    additional_care: Optional[AdditionalCare]= None
    observation: Optional[str]= None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class ObservationSlim(BaseModel):
    uuid: Optional[str] = None
    time: Optional[datetime] = None
    observation: Optional[str] = None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class ChildrenConfirmation(BaseModel):
    parent_email: str
    nursery_uuid: str
    child_uuid: str

class MediaSlim(BaseModel):
    uuid: str
    file:Optional[File]
    media_type:str
    time: datetime
    observation: Optional[str] = None
    date_added: datetime
    date_modified: datetime
    model_config = ConfigDict(from_attributes=True)

class ParentTransmissionsList(BaseModel):
    meals:Optional[list[MealSlim]] 
    activities:Optional[list[ActivitySlim]]
    naps:Optional[list[NapSlim]]
    health_records:Optional[list[HealthRecordSlim]] 
    hygiene_changes:Optional[list[HygieneChangeSlim]]
    media:Optional[list[MediaSlim]]
    observations:Optional[list[ObservationSlim]]
    model_config = ConfigDict(from_attributes=True)


class Transmission(BaseModel):
    uuid: str
    firstname: str
    lastname: str
    gender: str
    age:int = 0
    accepted_date:Optional[date]
    avatar:Optional[File] = None
    nb_parent: int
    meals:Optional[list[MealSlim]] 
    # activities:Optional[list[ActivitySlim]]
    naps:Optional[list[NapSlim]]
    health_records:Optional[list[HealthRecordSlim]] 
    hygiene_changes:Optional[list[HygieneChangeSlim]]
    media:Optional[list[MediaSlim]]
    observations:Optional[list[ObservationSlim]]
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class ChildTransmissionList(DataList):
    data: list[Transmission] = []
    model_config = ConfigDict(from_attributes=True)
class ChildDetailsList(DataList):
    data: list[ChildDetails] = []

    model_config = ConfigDict(from_attributes=True)


class ClientAccount(BaseModel):
    name: str
    account_number: str = ""
    entity_name: str = ""
    iban: str = ""
    address: str
    zip_code: str
    city: str
    country: str
    phone_number: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class ClientAccountUpdate(BaseModel):
    name: str
    account_number: str = ""
    entity_name: str = ""
    iban: str = ""
    address: str
    zip_code: str
    city: str
    country: str
    phone_number: str
    email: str

    model_config = ConfigDict(from_attributes=True)