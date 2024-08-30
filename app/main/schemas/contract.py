from datetime import datetime
from typing import Any, Optional, List
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.main import models
from app.main.models.db.session import SessionLocal
from app.main.schemas.parent import ParentResponse
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

class ContractUpdate(ContractBase):
    uuid: str
    status: Optional[str] = None

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

class ParentContractSchema(BaseModel):
    link: models.ParentRelationship = None
    firstname: str = None
    lastname: str = None
    birthplace: str = None
    fix_phone: str = None
    phone: str = None
    email: str = None
    recipient_number: str = None
    zip_code: str = None
    city: str = None
    country: str = None
    profession: str = None
    annual_income: float = 0
    company_name: str = None
    has_company_contract: bool = False
    dependent_children: int = 0
    disabled_children: int = 0

class ClientAccountContractSchema(BaseModel):
    uuid: str = None
    name: str = None
    iban: str = None
    bic: str = None
    rum: str = None
    signed_date: datetime = None

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
    tags: Optional[list[Tag]] = []
    typical_weeks: list[Any]
    parents: list[ParentResponse]=[]
    client_accounts: list[ClientAccountContractSchema]=[]

    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)


    @model_validator(mode='wrap')
    def validate_data(self, handler):
        validated_self = handler(self)
        session = SessionLocal()
        try:
            data = session.query(models.Contract).filter(models.Contract.nursery_uuid == validated_self.nursery_uuid).first()

            for parent in data.parents:
                exist_parent = session.query(models.Parent).\
                    filter(models.Parent.uuid == parent.uuid).\
                    filter(models.Parent.status.not_in(["DELETED"])).\
                        first()
                if not exist_parent:
                    raise ValueError("Parent not found.")
                
            # values["has_pickup_child_authorization"] = False
            # values["has_app_authorization"] = False
    
            
            return 
        except Exception as e:
            print("Error getting data: " + str(e))
        finally:
            session.close()


class ContractMini(BaseModel):
    uuid: str
    child: Optional[ChildMini3] = None
    begin_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    has_company_contract: Optional[bool] = False
    type: Optional[str] = None
    status: Optional[str] = None
    hourly_volume: Optional[float] = 0
    tags:Optional[list[Tag]] = []

    model_config = ConfigDict(from_attributes=True)

class ContractSlimList(DataList):

    data: List[ContractMini] = []
class ContractList(DataList):

    data: List[Contract] = []
    