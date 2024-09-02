from datetime import datetime
from typing import Any, Optional, List
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, model_validator

from app.main import models
from app.main.core.i18n import __
from app.main.models.db.session import SessionLocal
from app.main.schemas.invoice import InvoiceMiniDetails
from app.main.schemas.parent import Avatar, ParentResponse
from app.main.schemas.preregistration import ChildMini3, TimeSlotInputSchema
from app.main.schemas.tag import Tag

# from .nursery import NurserySlim
from .base import DataList


class ContractBase(BaseModel):
    nursery_uuid: str 
    begin_date: datetime
    end_date: datetime
    type: str
    annual_income: Optional[float] = 0
    caution: Optional[float] = 0
    reference: Optional[str] = None
    note: Optional[str] = None
    has_company_contract: bool = False

    child_uuid: str
    client_account_uuid: Optional[str] = None
    sepa_direct_debit_uuid: Optional[str] = None
    parent_uuids: list[str]

class ContractCreate(ContractBase):
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

class ContractUpdate(BaseModel):
    uuid: str

    status: Optional[str] = None

    typical_weeks: list[list[list[TimeSlotInputSchema]]]

    @field_validator('typical_weeks')
    def validate_week_length(cls, value):
        for week in value:
            if len(week) > 5:
                raise HTTPException(status_code=422, detail=("Each week's data list cannot exceed 5 items"))
        return value

    # @field_validator("end_date")
    # def validate_end_date(cls, value, values):
    #     begin_date = values.data.get('begin_date')
    #     if value <= begin_date:
    #         raise ValueError("End date must be after to begin date.")
    #     return value
class ProlongeContract(BaseModel):
    uuid: str
    child_uuid: str
    end_date: datetime


class ParentContractSchema(BaseModel):
    uuid:str
    avatar : Optional[Avatar] = None
    firstname: Optional[str]=None
    lastname: Optional[str]=None
    fix_phone:Optional[str] = None
    phone:Optional[str] = None
    link: Optional[models.ParentRelationship] = None
    email: Optional[EmailStr]= None
    profession: Optional[str]=None
    annual_income: Optional[float] = None
    company_name: Optional[str]= None
    has_company_contract: Optional[bool] = None
    dependent_children: Optional[int] = None
    disabled_children: Optional[int] = None
    has_pickup_child_authorization: bool= False
    has_app_authorization: bool = False
    
    model_config = ConfigDict(from_attributes=True)


class ClientAccountContractUpdate(BaseModel):
    uuid: str
    contract_uuid: str
    name: Optional[str]
    iban: Optional[str]
    bic: Optional[str]
    rum: Optional[str]

class ClientAccountContractSchema(BaseModel):
    uuid: Optional[str] = None
    name: Optional[str] = None
    iban: Optional[str] = None
    bic: Optional[str] = None
    rum: Optional[str] = None
    signed_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Contract(BaseModel):
    uuid: Optional[str] = None
    nursery_uuid: str 
    child: Optional[ChildMini3] = None
    begin_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    type: Optional[str] = None
    has_company_contract: Optional[bool] = False
    status: Optional[str] = None
    hourly_volume: Optional[float] = 0
    tags: Optional[list[Tag]]=None
    typical_weeks: list[Any]
    parents: list[ParentContractSchema]=None
    client_account: Optional[ClientAccountContractSchema]=None
    invoices: list[InvoiceMiniDetails]=None

    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)


class ContractMini(BaseModel):
    uuid: str
    child: Optional[ChildMini3] = None
    begin_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    has_company_contract: Optional[bool] = False
    type: Optional[str] = None
    status: Optional[str] = None
    hourly_volume: Optional[float] = 0
    tags:Optional[list[Tag]] =None

    model_config = ConfigDict(from_attributes=True)

class ContractSlimList(DataList):

    data: List[ContractMini] = []
class ContractList(DataList):

    data: List[Contract] = []
    