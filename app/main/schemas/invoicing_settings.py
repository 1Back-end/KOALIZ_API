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

"""
QuoteSetting model
class QuoteSetting(Base):
    __tablename__ = "quote_settings"

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    adaptation_type: str = Column(types.Enum(AdaptationType), default=AdaptationType.PACKAGE, nullable=False)
    adaptation_package_costs: float = Column(Float, default=150)
    adaptation_package_days: float = Column(Float, default=5)
    adaptation_hourly_rate: float = Column(Float, default=10)
    adaptation_hours_number: int = Column(Integer, default=120)

    hourly_rate_ranges: Mapped[list[any]] = relationship("HourlyRateRange", back_populates="quote_setting", uselist=True, order_by="HourlyRateRange.number_of_hours")

    has_deposit: bool = Column(Boolean, default=True)
    deposit_type: str = Column(types.Enum(DepositType), default=DepositType.PERCENTAGE, nullable=False)
    deposit_percentage: float = Column(Float, default=30)
    deposit_value: float = Column(Float, default=0.3)

    has_registration_fee: bool = Column(Boolean, default=True)
    registration_fee: float = Column(Float, default=90)

    last_special_month: bool = Column(Boolean, default=True)
    min_days_for_last_special_month: int = Column(Integer, default=5)

    # Invoice
    desired_text_on_invoice_line: str = Column(String, nullable=True)
    # display_calculation_details_in_invoice: bool = Column(Boolean, default=False)
    invoicing_time: str = Column(types.Enum(InvoiceTimeType), default=InvoiceTimeType.END_OF_MONTH, nullable=False)
    invoice_payable_within: int = Column(Integer, default=0)
    terms_and_conditions_displayed_on_invoice: str = Column(String, nullable=True)
    invoice_footer: str = Column(String, nullable=True)

    is_overrun_billed: bool = Column(Boolean, default=True)
    overrun_amount: float = Column(Float, default=0)

    daily_meal_charges: float = Column(Float, default=0)
    daily_medical_expenses: float = Column(Float, default=0)
    daily_other_expenses: float = Column(Float, default=0)
    # Invoice

    is_default: bool = Column(Boolean, default=False)

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

HourlyRateRange model

class HourlyRateRange(Base):
    __tablename__ = "hourly_rate_ranges"

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    number_of_day: int = Column(Integer, default=0, unique=True)
    number_of_hours: float = Column(Float)
    hourly_rate: float = Column(Float, default=10)

    quote_setting_uuid: str = Column(String, ForeignKey('quote_settings.uuid'), nullable=True)
    quote_setting: Mapped[any] = relationship("QuoteSetting", foreign_keys=quote_setting_uuid, back_populates="hourly_rate_ranges", uselist=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


"""


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
