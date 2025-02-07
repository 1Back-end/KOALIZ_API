from typing import Optional, Any

from fastapi import Body, HTTPException, Query
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, model_validator
from datetime import datetime, time, date

from app.main import models
from app.main.core.i18n import __
from app.main.schemas import DataList, NurseryMini, Tag
from app.main.schemas.base import Items
from app.main.schemas.file import File


class QuotePreContract(BaseModel):
    typical_weeks: list[Any]

    model_config = ConfigDict(from_attributes=True)


class PreregistrationMini(BaseModel):
    uuid: str
    nursery: NurseryMini
    note: str = None
    status: str = None

    model_config = ConfigDict(from_attributes=True)


class QuoteChildMini(BaseModel):
    uuid: str
    firstname: str
    lastname: str
    gender: models.Gender
    birthdate: date
    birthplace: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class QuoteNurseryMini(BaseModel):
    uuid: str
    name: str
    model_config = ConfigDict(from_attributes=True)


class CMG(BaseModel):
    amount: float = 0
    family_type: models.FamilyType = None
    number_children: int = 0
    annual_income: float = 0
    band_number: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class QuoteTimeTableItem(BaseModel):
    title_fr: str
    title_en: str
    amount: float = 0
    type: models.QuoteTimetableItemType

    model_config = ConfigDict(from_attributes=True)


class QuoteTimetable(BaseModel):
    date_to: date
    amount: float = 0
    items: list[QuoteTimeTableItem] = []

    model_config = ConfigDict(from_attributes=True)


class QuotePreregistrationMini(BaseModel):
    uuid: str
    tags: Optional[list[Tag]] = []
    model_config = ConfigDict(from_attributes=True)


class QuoteDetails(BaseModel):
    uuid: str
    child: QuoteChildMini
    nursery: QuoteNurseryMini
    pre_contract: QuotePreContract
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
    preregistration: QuotePreregistrationMini

    timetables: list[QuoteTimetable] = []

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
    preregistration_uuid: str
    child: QuoteChildSlim
    pre_contract: QuotePreContractSlim

    model_config = ConfigDict(from_attributes=True)


class QuoteList(DataList):
    data: list[QuoteSlim] = []

    model_config = ConfigDict(from_attributes=True)


class CMGUpdate(BaseModel):
    family_type: models.FamilyType = None
    number_children: int = 0
    annual_income: float = 0

    model_config = ConfigDict(from_attributes=True)


class QuoteSettingsUpdate(BaseModel):
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


class CMGAmountRange(BaseModel):
    uuid: str
    lower: float
    upper: float
    family_type: models.FamilyType
    number_children: int

    model_config = ConfigDict(from_attributes=True)


class CMGAmountRangeUpdate(BaseModel):
    lower: float
    upper: float
    family_type: models.FamilyType
    number_children: int

    model_config = ConfigDict(from_attributes=True)


class CMGAmount(BaseModel):
    uuid: str
    child_age_lower: int
    child_age_upper: int
    tranche_1_amount: float
    tranche_2_amount: float
    tranche_3_amount: float
    govt_update_of: Optional[date]
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)


class CMGAmountUpdate(BaseModel):
    child_age_lower: int
    child_age_upper: int
    tranche_1_amount: float
    tranche_2_amount: float
    tranche_3_amount: float
    govt_update_of: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
