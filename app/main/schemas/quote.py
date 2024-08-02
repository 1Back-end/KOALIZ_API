from typing import Optional, Any

from fastapi import Body, HTTPException, Query
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, model_validator
from datetime import datetime, time, date

from app.main import models
from app.main.core.i18n import __
from app.main.schemas import DataList, NurseryMini
from app.main.schemas.base import Items
from app.main.schemas.file import File


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


class QuoteDetails(BaseModel):
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


class QuoteChildMini(BaseModel):
    uuid: str
    firstname: str
    lastname: str
    gender: models.Gender
    birthdate: date
    birthplace: str
    date_added: datetime
    date_modified: datetime
    model_config = ConfigDict(from_attributes=True)


class QuoteDetails(BaseModel):
    uuid: str
    code: str
    child: QuoteChildMini
    nursery: NurseryMini
    pre_contract: PreContract
    note: str = None
    status: str = None
    accepted_date: Optional[datetime] = None
    refused_date: Optional[datetime] = None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)


class QuoteChildSlim(BaseModel):
    uuid: str
    firstname: str
    lastname: str
    gender: models.Gender
    birthdate: date

    model_config = ConfigDict(from_attributes=True)


class QuotePreContractSlim(BaseModel):
    begin_date: date
    end_date: date

    model_config = ConfigDict(from_attributes=True)


class QuoteSlim(BaseModel):
    uuid: str
    first_month_cost: float = 0
    monthly_cost: float = 0
    total_cost: float = 0
    status: str = None
    child: QuoteChildSlim
    pre_contract: QuotePreContractSlim

    model_config = ConfigDict(from_attributes=True)

class QuoteList(DataList):
    data: list[QuoteSlim] = []

    model_config = ConfigDict(from_attributes=True)

