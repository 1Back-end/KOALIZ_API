from typing import Optional, Any

from fastapi import Body, HTTPException, Query
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator, AliasPath
from datetime import datetime, time, date

from app.main import models
from app.main.core.i18n import __
from app.main.schemas.base import Items, DataList
from app.main.schemas.file import File


class InvoicePreContract(BaseModel):
    typical_weeks: list[Any]

    model_config = ConfigDict(from_attributes=True)


class PreregistrationMini(BaseModel):
    uuid: str
    note: str = None
    status: str = None

    model_config = ConfigDict(from_attributes=True)


class InvoiceChildMini(BaseModel):
    uuid: str
    firstname: str
    lastname: str
    gender: models.Gender
    birthdate: date
    model_config = ConfigDict(from_attributes=True)


class CMG(BaseModel):
    amount: float = 0
    family_type: models.FamilyType = None
    number_children: int = 0
    annual_income: float = 0
    band_number: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class InvoiceTimeTableItem(BaseModel):
    title_fr: str
    title_en: str
    amount: float = 0

    model_config = ConfigDict(from_attributes=True)


class InvoiceTimetable(BaseModel):
    date_to: date
    amount: float = 0
    items: list[InvoiceTimeTableItem] = []

    model_config = ConfigDict(from_attributes=True)


class InvoiceDetails(BaseModel):
    uuid: str
    child: InvoiceChildMini
    pre_contract: InvoicePreContract
    cmg: Optional[CMG] = None
    status: str = None
    hourly_rate: float = 0
    registration_fee: float = 0

    deposit_type: models.DepositType
    deposit_percentage: float = 0
    deposit_value: float = 0

    adaptation_type: models.AdaptationType
    adaptation_hourly_rate: float = 0
    adaptation_hours_number: int = 0
    adaptation_package_costs: float = 0
    adaptation_package_days: int = 0

    monthly_billed_hours: Optional[float]
    smoothing_months: Optional[float]
    weeks_in_smoothing: Optional[float]
    deductible_weeks: Optional[float]
    total_closing_days: Optional[int]

    timetables: list[InvoiceTimetable] = []

    model_config = ConfigDict(from_attributes=True)


class InvoiceChildSlim(BaseModel):
    uuid: str
    firstname: str
    lastname: str
    gender: models.Gender
    birthdate: date

    model_config = ConfigDict(from_attributes=True)


class InvoicePreContractSlim(BaseModel):
    begin_date: date
    end_date: date

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


class CMGUpdate(BaseModel):
    family_type: models.FamilyType = None
    number_children: int = 0
    annual_income: float = 0

    model_config = ConfigDict(from_attributes=True)


class InvoiceSettingsUpdate(BaseModel):
    hourly_rate: float = 0
    registration_fee: float = 0

    deposit_type: models.DepositType
    deposit_percentage: float = 0
    deposit_value: float = 0

    adaptation_type: models.AdaptationType
    adaptation_hourly_rate: float = 0
    adaptation_hours_number: int = 0
    adaptation_package_costs: float = 0
    adaptation_package_days: int = 0

    model_config = ConfigDict(from_attributes=True)
