from enum import Enum

from datetime import datetime, date, time
from sqlalchemy import ARRAY, Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, event, Time, types, \
    UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship, Mapped
from .db.base_class import Base


class NurseryStatusType(str, Enum):
    ACTIVED = "ACTIVED"
    UNACTIVED = "UNACTIVED"
    DELETED = "DELETED"

class QuoteTimetableItemType(str, Enum):
    REGISTRATION = "REGISTRATION"
    DEPOSIT = "DEPOSIT"
    ADAPTATION = "ADAPTATION"
    INVOICE = "INVOICE"
    CUSTOM = "CUSTOM"
    OVERTIME = "OVERTIME"


class FamilyType(Enum):
    SINGLE_PARENT = "SINGLE_PARENT"
    COUPLE = "COUPLE"


class AdaptationType(Enum):
    PACKAGE = "PACKAGE"
    HOURLY = "HOURLY"


class DepositType(Enum):
    PERCENTAGE = "PERCENTAGE"
    VALUE = "VALUE"


class Quote(Base):
    """
     database model for storing Nursery related details
    """
    __tablename__ = 'quotes'

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    title: str = Column(String, nullable=False, default="")

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    parent_guest_uuid: str = Column(String, ForeignKey('parent_guests.uuid'), nullable=True)
    parent_guest: Mapped[any] = relationship("ParentGuest", foreign_keys=parent_guest_uuid, uselist=False)

    child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=True)
    child: Mapped[any] = relationship("Child", foreign_keys=child_uuid, uselist=False)

    pre_contract_uuid: str = Column(String, ForeignKey('pre_contracts.uuid'), nullable=True)
    pre_contract: Mapped[any] = relationship("PreContract", foreign_keys=pre_contract_uuid, uselist=False)

    hourly_rate: float = Column(Numeric(precision=10, scale=2), default=10)

    has_registration_fee: bool = Column(Boolean, default=True)
    registration_fee: float = Column(Numeric(precision=10, scale=2), default=90)

    has_deposit: bool = Column(Boolean, default=True)
    deposit_type: str = Column(types.Enum(DepositType), default=DepositType.PERCENTAGE, nullable=False)
    deposit_percentage: float = Column(Numeric(precision=10, scale=4), default=0.3)
    deposit_value: float = Column(Numeric(precision=10, scale=4), default=0.3)

    adaptation_type: str = Column(types.Enum(AdaptationType), default=AdaptationType.PACKAGE, nullable=False)
    adaptation_package_costs: float = Column(Numeric(precision=10, scale=2), default=150)
    adaptation_package_days: int = Column(Integer, default=5)
    adaptation_hours_number: int = Column(Integer, default=120)
    adaptation_hourly_rate: float = Column(Numeric(precision=10, scale=2), default=10)

    quote_cmg_uuid: str = Column(String, ForeignKey('quote_cmgs.uuid'), nullable=True)
    quote_cmg: Mapped[any] = relationship("QuoteCMG", foreign_keys=quote_cmg_uuid, uselist=False)

    quote_setting_uuid: str = Column(String, ForeignKey('quote_settings.uuid'), nullable=True)
    quote_setting: Mapped[any] = relationship("QuoteSetting", foreign_keys=quote_setting_uuid, uselist=False)

    timetables: Mapped[list[any]] = relationship("QuoteTimetable", back_populates="quote", uselist=True) #Echeancier

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(Quote, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(Quote, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


class QuoteTimetable(Base):
    """
     database model for storing Timetable related details
    """
    __tablename__ = "quote_timetables"

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    date_to: date = Column(Numeric(precision=10, scale=2), nullable=0)
    amount: float = Column(Numeric(precision=10, scale=2), nullable=0)
    items: Mapped[list[any]] = relationship("QuoteTimetableItem", back_populates="quote", uselist=True)

    quote_uuid: str = Column(String, ForeignKey('quotes.uuid'), nullable=True)
    quote: Mapped[any] = relationship("Quote", foreign_keys=quote_uuid, uselist=False, back_populates="timetables")

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(QuoteTimetable, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(QuoteTimetable, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


class QuoteTimetableItem(Base):
    """
     database model for storing Timetable related details
    """
    __tablename__ = "quote_timetable_items"

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    title: str = Column(String, nullable=False)
    type: str = Column(types.Enum(QuoteTimetableItemType), nullable=False)
    amount: float = Column(Numeric(precision=10, scale=2), nullable=0)

    quote_timetable_uuid: str = Column(String, ForeignKey('quote_timetables.uuid'), nullable=True)
    quote_timetable: Mapped[any] = relationship("QuoteTimetable", foreign_keys=quote_timetable_uuid, uselist=False, back_populates="items")

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(QuoteTimetableItem, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(QuoteTimetableItem, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


class QuoteCMG(Base):
    """
     database model for storing HourlyRate Opening Hour related details
    """
    __tablename__ = "quote_cmgs"

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    name: str = Column(String)
    amount: float = Column(Numeric(precision=10, scale=2), nullable=0)
    family_type: str = Column(types.Enum(FamilyType), default=FamilyType.COUPLE, nullable=False)
    number_children: int = Column(Integer, default=1)
    annual_income: float = Column(Numeric(precision=10, scale=2), default=0)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(QuoteCMG, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(QuoteCMG, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


class QuoteSetting(Base):
    """
     database model for storing Quote Settings Opening Hour related details
    """
    __tablename__ = "quote_settings"

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    adaptation_type: str = Column(types.Enum(AdaptationType), default=AdaptationType.PACKAGE, nullable=False)
    adaptation_package_costs: float = Column(Numeric(precision=10, scale=2), default=150)
    adaptation_package_days: float = Column(Numeric(precision=10, scale=2), default=5)
    adaptation_hourly_rate: float = Column(Numeric(precision=10, scale=2), default=10)

    hourly_rate_ranges: Mapped[any] = relationship("HourlyRateRange", back_populates="quote_setting", uselist=True)

    has_deposit: bool = Column(Boolean, default=True)
    deposit_type: str = Column(types.Enum(DepositType), default=DepositType.PERCENTAGE, nullable=False)
    deposit_percentage: float = Column(Numeric(precision=10, scale=4), default=0.3)
    deposit_value: float = Column(Numeric(precision=10, scale=4), default=0.3)

    has_registration_fee: bool = Column(Boolean, default=True)
    registration_fee: float = Column(Numeric(precision=10, scale=2), default=90)

    last_special_month: bool = Column(Boolean, default=True)
    min_days_for_last_special_month: int = Column(Integer, default=5)

    # Invoice
    desired_text_on_invoice_line: str = Column(String, nullable=True)
    display_calculation_details_in_invoice: bool = Column(Boolean, default=False)
    invoicing_time: str = Column(String, nullable=True)
    invoice_payable_within: int = Column(Integer, default=0)
    terms_and_conditions_displayed_on_invoice: str = Column(String, nullable=True)
    invoice_footer: str = Column(String, nullable=True)

    is_overrun_billed: bool = Column(Boolean, default=True)
    overrun_amount: float = Column(Numeric(precision=10, scale=2), default=0)

    daily_meal_charges: float = Column(Numeric(precision=10, scale=2), default=0)
    daily_medical_expenses: float = Column(Numeric(precision=10, scale=2), default=0)
    daily_other_expenses: float = Column(Numeric(precision=10, scale=2), default=0)
    # Invoice

    is_default: bool = Column(Boolean, default=False)

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(QuoteSetting, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(QuoteSetting, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


class HourlyRateRange(Base):
    """
     database model for storing HourlyRate Opening Hour related details
    """
    __tablename__ = "hourly_rate_ranges"

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    number_of_day: int = Column(Integer, default=0, unique=True)
    number_of_hours: time = Column(Time)
    hourly_rate: float = Column(Numeric(precision=10, scale=2), default=10)

    quote_setting_uuid: str = Column(String, ForeignKey('quote_settings.uuid'), nullable=True)
    quote_setting: Mapped[any] = relationship("QuoteSetting", foreign_keys=quote_setting_uuid, back_populates="hourly_rate_ranges", uselist=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(HourlyRateRange, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(HourlyRateRange, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


class CMGAmountRange(Base):
    """
     database model for storing HourlyRate Opening Hour related details
    """
    __tablename__ = "cmg_amount_ranges"

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    lower: float = Column(Numeric(precision=10, scale=2), default=0)
    upper: float = Column(Numeric(precision=10, scale=2), nullable=0)
    family_type: str = Column(types.Enum(FamilyType), default=FamilyType.COUPLE, nullable=False)
    number_children: int = Column(Integer, default=1)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    UniqueConstraint("family_type", "number_children", name="family_type_number_children_unique")
    UniqueConstraint("family_type", "number_children", name="family_type_number_children_unique")


@event.listens_for(CMGAmountRange, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(CMGAmountRange, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


class CMGAmount(Base):
    """
     database model for storing HourlyRate Opening Hour related details
    """
    __tablename__ = "cmg_amounts"

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    child_age_lower: int = Column(Integer, nullable=0)
    child_age_upper: int = Column(Integer, nullable=0)
    tranche_1_amount: float = Column(Numeric(precision=10, scale=2), nullable=0, unique=True)
    tranche_2_amount: float = Column(Numeric(precision=10, scale=2), nullable=0, unique=True)
    tranche_3_amount: float = Column(Numeric(precision=10, scale=2), nullable=0, unique=True)
    govt_update_of: date = Column(Date, nullable=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(CMGAmountRange, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(CMGAmountRange, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()
