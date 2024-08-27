import math
from typing import Optional, Any

from fastapi import Body, HTTPException, Query
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator, AliasPath, computed_field
from datetime import datetime, time, date

from app.main import models
from app.main.core.i18n import __
from app.main.schemas import AddressBase
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
    uuid: str
    title_fr: str
    title_en: str
    amount: float = 0
    total_hours: Optional[float] = None
    unit_price: Optional[float] = None

    @model_validator(mode='wrap')
    def round_hours(self, handler):
        validated_self = handler(self)
        validated_self.total_hours = round(validated_self.total_hours, 2)

        return validated_self

    model_config = ConfigDict(from_attributes=True)


class InvoiceContract(BaseModel):
    reference: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class InvoiceNursery(BaseModel):
    uuid: str
    name: str
    phone_number: str
    address: AddressBase = None

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
    uuid: Optional[str]
    name: Optional[str]
    account_number: Optional[str]
    entity_name: Optional[str]
    iban: Optional[str]
    address: Optional[str]
    zip_code: Optional[str]
    city: Optional[str]
    country: Optional[str]
    phone_number: Optional[str]
    email: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class PaymentSlim(BaseModel):
    uuid: str
    type: models.PaymentType
    method: models.PaymentMethod
    amount: float
    date_added: datetime


class InvoiceDetails(BaseModel):
    uuid: str
    date_to: date
    amount: float = 0
    status: str = None
    reference: str
    invoicing_period_start: Optional[date]
    invoicing_period_end: Optional[date]

    nursery: InvoiceNursery
    contract: InvoiceContract
    parent_guest: InvoiceParentGuest
    client_account: Optional[InvoiceClientAccount] = None

    items: list[InvoiceTimeTableItem] = []
    invoices_statistic: dict[str, float] = {}
    payments: list[PaymentSlim] = []

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


class DashboardInvoiceTimetableSlim(BaseModel):
    uuid: str
    reference: str
    amount: float = 0
    status: str
    total_hours: float = 0
    total_overtime_hours: float = 0
    child: InvoiceChildSlim

    @computed_field(return_type=float)
    @property
    def sum_hours(self):
        return self.total_hours + self.total_overtime_hours

    @model_validator(mode='wrap')
    def round_hours(self, handler):
        validated_self = handler(self)
        validated_self.total_hours = round(validated_self.total_hours, 2)
        validated_self.total_overtime_hours = round(validated_self.total_overtime_hours, 2)

        return validated_self

    model_config = ConfigDict(from_attributes=True)


class DashboardInvoiceList(DataList):
    data: list[DashboardInvoiceTimetableSlim] = []

    model_config = ConfigDict(from_attributes=True)


class PaymentBase(BaseModel):
    type: models.PaymentType
    method: models.PaymentMethod
    amount: Optional[float] = Field(None, gt=0)

    @model_validator(mode="wrap")
    def validate_amount(self, handler):
        validated_self = handler(self)
        if validated_self.type == models.PaymentType.PARTIAL and not validated_self.amount:
            raise ValueError(__("amount-required"))
        return validated_self


class PaymentCreate(PaymentBase):
    pass


class Payment(PaymentBase):
    uuid: str

    model_config = ConfigDict(from_attributes=True)


class ItemsCreateUpdate(BaseModel):
    uuid: Optional[str] = None
    title_fr: str
    title_en: str
    # amount: float
    total_hours: Optional[float] = None
    unit_price: float
    type: Optional[models.InvoiceItemType] = None

    model_config = ConfigDict(from_attributes=True)


class InvoiceUpdate(BaseModel):
    items: list[ItemsCreateUpdate] = []
    uuids_to_delete: list[str] = []


class InvoiceCreate(BaseModel):
    invoice_uuid: str
    date_to: Optional[date] = None
    invoicing_period_start: Optional[date] = None
    invoicing_period_end: Optional[date] = None
    items: list[ItemsCreateUpdate] = []


class NurserySale(BaseModel):
    uuid: str
    name: str
    current_month: float
    previous_month: float

    model_config = ConfigDict(from_attributes=True)
