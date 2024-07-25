from typing import Optional
from pydantic import BaseModel, ConfigDict,EmailStr, model_validator, root_validator, validator
from datetime import datetime, date
from .tag import Tag
from app.main.models.db.session import SessionLocal
from app.main.models import tag
from app.main.models.membership import MembershipType


class MembershipBase(BaseModel):
    # owner_uuid: str
    period_from:datetime
    period_to: datetime
    period_unit:str 
    nursery_uuid: str
    membership_uuid:str
    # membership_type_uuid: str

class MembershipCreate(MembershipBase):
    period_unit:MembershipType

# class NurseryMembershipSim(BaseModel):
#     membership_uuid:str
#     period_from:datetime
#     period_to: datetime
#     period_unit:Optional[MembershipType] 
#     nursery_uuid: str

# class AddNurseryMemberships(BaseModel):
#     memberships:list[NurseryMembershipSim]

class MembershipUpdate(BaseModel):
    uuid:str
    period_unit:Optional[MembershipType] = None
    period_from: Optional[datetime] = None
    period_to: Optional[datetime] = None
    nursery_uuid: str 
    membership_type_uuid:Optional[str]  = None

class MembershipTypeSlim(BaseModel):
    uuid: Optional[str]=None
    title_fr: Optional[str] =None
    title_en: Optional[str] =None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class Nursery2(BaseModel):
    uuid: str
    email: EmailStr
    name: str
    # logo: Optional[File]
    # signature: Optional[File]
    # stamp: Optional[File]
    memberships:Optional[list[MembershipTypeSlim]] =[]
    total_places: int = 0
    phone_number: str
    # address: Address
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)



class Owner2(BaseModel):
    uuid: Optional[str] = None
    email: EmailStr
    firstname: str
    lastname: str
    status: str
    # avatar: Optional[File]
    # added_by: Optional[AddedBy]
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class MembershipResponse(MembershipBase):
    uuid: str
    status: str
    duration:float
    nursery:Nursery2
    date_added: datetime
    date_modified: datetime
    model_config = ConfigDict(from_attributes=True)


class MembershipResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page:int
    data: list[MembershipResponse] =[]

    model_config = ConfigDict(from_attributes=True)

