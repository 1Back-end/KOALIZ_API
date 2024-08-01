from dataclasses import dataclass
from datetime import date, datetime
import jwt
import pytz
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, Date, ForeignKey, String, Integer, DateTime
from sqlalchemy import event

from app.main.models.db.base_class import Base


@dataclass
class Year(Base):

    """ Year Model for storing years related details """

    __tablename__ = "years"

    uuid = Column(String, primary_key=True, unique=True)

    year: int = Column(Integer, nullable=False, default=2024)

    date_added: any = Column(DateTime, server_default=func.now())
    date_modified: any = Column(DateTime, server_default=func.now())

@event.listens_for(Year, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the create/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()

@event.listens_for(Year, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()

@dataclass
class Month(Base):

    """ Month Model for storing months related details """

    __tablename__ = "months"

    uuid = Column(String, primary_key=True, unique=True)
    start_date: date = Column(Date, nullable=False)
    end_date: date = Column(Date, nullable=False)

    year_uuid: str = Column(String, ForeignKey('years.uuid'), nullable=True)
    year = relationship("Year", foreign_keys=[year_uuid], uselist=False)

    date_added: any = Column(DateTime, server_default=func.now())
    date_modified: any = Column(DateTime, server_default=func.now())

@event.listens_for(Month, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the create/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()

@event.listens_for(Month, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()

@dataclass
class Week(Base):

    """ Week Model for storing weeks related details """

    __tablename__ = "weeks"

    uuid = Column(String, primary_key=True, unique=True)
    start_date: date = Column(Date, nullable=False)
    end_date: date = Column(Date, nullable=False)
    week_index: int = Column(Integer, nullable=False)

    month_uuid: str = Column(String, ForeignKey('months.uuid'), nullable=True)
    month = relationship("Month", foreign_keys=[month_uuid], uselist=False)

    date_added: any = Column(DateTime, server_default=func.now())
    date_modified: any = Column(DateTime, server_default=func.now())

@event.listens_for(Week, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the create/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()

@event.listens_for(Week, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()

@dataclass
class Day(Base):

    """ Day Model for storing days related details """

    __tablename__ = "days"

    uuid = Column(String, primary_key=True, unique=True)
    day: date = Column(Date, nullable=False)
    day_of_week: str = Column(String, nullable=False)

    month_uuid: str = Column(String, ForeignKey('months.uuid'), nullable=True)
    month = relationship("Month", foreign_keys=[month_uuid], uselist=False)

    year_uuid: str = Column(String, ForeignKey('years.uuid'), nullable=True)
    year = relationship("Year", foreign_keys=[year_uuid], uselist=False)

    week_uuid: str = Column(String, ForeignKey('weeks.uuid'), nullable=True)
    week = relationship("Week", foreign_keys=[week_uuid], uselist=False)

    date_added: any = Column(DateTime, server_default=func.now())
    date_modified: any = Column(DateTime, server_default=func.now())

@event.listens_for(Day, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the create/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()

@event.listens_for(Day, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()
