from typing import Optional, Any

from fastapi import Body, HTTPException, Query
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator, AliasPath
from datetime import datetime, time, date

from app.main import models
from app.main.core.i18n import __
from app.main.schemas.base import Items, DataList
from app.main.schemas.file import File


class InvoiceChildMini(BaseModel):
    uuid: str
    firstname: str
    lastname: str
    gender: models.Gender
    birthdate: date
    model_config = ConfigDict(from_attributes=True)


class InvoiceTimeTableItem(BaseModel):
    title_fr: str
    title_en: str
    amount: float = 0
    total_hours: Optional[float] = None
    unit_price: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class InvoiceContract(BaseModel):
    reference: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class InvoiceNursery(BaseModel):
    uuid: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class InvoiceParentGuest(BaseModel):
    firstname: str
    lastname: str
    fix_phone: str = None
    phone: str
    email: EmailStr
    zip_code: str
    city: str
    country: str
    company_name: str
    has_company_contract: bool

    model_config = ConfigDict(from_attributes=True)

class InvoiceClientAccount(BaseModel):
    name: str
    account_number: str
    entity_name: str
    iban: str
    address: str
    zip_code: str
    city: str
    country: str
    phone_number: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class InvoiceDetails(BaseModel):
    uuid: str
    date_to: date
    amount: float = 0
    status: str = None
    reference: str
    invoicing_period_start: Optional[date]
    invoicing_period_end: Optional[date]

    contract: InvoiceContract
    parent_guest: InvoiceParentGuest
    client_account: Optional[InvoiceClientAccount] = None

    items: list[InvoiceTimeTableItem] = []

    model_config = ConfigDict(from_attributes=True)


class InvoiceChildSlim(BaseModel):
    uuid: str
    firstname: str
    lastname: str
    gender: models.Gender
    birthdate: date

    model_config = ConfigDict(from_attributes=True)


class InvoiceTimetableSlim(BaseModel):
    uuid: str
    # child: InvoiceChildSlim = Field(alias="invoice_timetables.invoice.child")
    reference: str
    date_to: date = None
    amount_paid: float = 0
    amount_due: float = 0
    amount: float = 0
    status: str
    child: InvoiceChildSlim
    # pre_contract: InvoicePreContractSlim

    model_config = ConfigDict(from_attributes=True)


class InvoiceList(DataList):
    data: list[InvoiceTimetableSlim] = []

    model_config = ConfigDict(from_attributes=True)
