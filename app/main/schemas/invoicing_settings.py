from typing import Optional, Literal

from fastapi import Body
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, model_validator
from datetime import datetime, time

from app.main import models
from app.main.core.i18n import __
from app.main.schemas import File, DataList, Address, AddressCreate, AddressUpdate
from app.main.schemas.address import AddressSLim
from app.main.schemas.nursery_close_hours import NurseryCloseHourDetails
from app.main.schemas.nursery_holidays import NurseryHolidaysDetails
from app.main.schemas.user import AddedBy
from app.main.schemas.membership import MembershipTypeSlim


class HourlyRateRangeBase(BaseModel):
    number_of_day: int
    number_of_hours: float
    hourly_rate: float


class HourlyRateRangeCreate(HourlyRateRangeBase):
    quote_setting_uuid: str


class HourlyRateRangeUpdate(HourlyRateRangeBase):
    quote_setting_uuid: str


class HourlyRateRangeDetails(HourlyRateRangeBase):
    uuid: str

    model_config = ConfigDict(from_attributes=True)


class QuoteSettingBase(BaseModel):
    adaptation_type: models.AdaptationType
    adaptation_package_costs: float = 0
    adaptation_package_days: float = 0
    adaptation_hourly_rate: float = 0
    adaptation_hours_number: int = 0
    has_deposit: bool = True
    deposit_type: models.DepositType
    deposit_percentage: float = 0
    deposit_value: float = 0
    has_registration_fee: bool = True
    registration_fee: float = 0
    last_special_month: bool = True
    min_days_for_last_special_month: int = 0
    desired_text_on_invoice_line: str = ""
    invoicing_time: models.InvoiceTimeType
    invoice_payable_within: int = 0
    terms_and_conditions_displayed_on_invoice: str = ""
    invoice_footer: str = ""
    is_overrun_billed: bool = True
    overrun_amount: float = 0
    daily_meal_charges: float = 0
    daily_medical_expenses: float = 0
    daily_other_expenses: float = 0


class QuoteSettingCreate(QuoteSettingBase):
    nursery_uuid: str


class QuoteSettingUpdate(QuoteSettingBase):
    nursery_uuid: str


class QuoteSettingDetails(QuoteSettingBase):
    uuid: str
    is_default: bool = False
    hourly_rate_ranges: list[HourlyRateRangeDetails]
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)


class QuoteSettingList(DataList):
    data: list[QuoteSettingDetails]

    model_config = ConfigDict(from_attributes=True)
