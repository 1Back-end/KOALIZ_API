from dataclasses import dataclass
from datetime import date
from sqlalchemy.sql import func
from sqlalchemy import Column, Date, ForeignKey, String, Integer, DateTime
from sqlalchemy import event
from sqlalchemy.orm import relationship, Mapped

from app.main.models.db.base_class import Base



@dataclass
class Year(Base):

    """ Year Model for storing years related details """

    __tablename__ = "years"

    uuid = Column(String, primary_key=True, unique=True)

    year: int = Column(Integer, nullable=False, default=2024)

    date_added: any = Column(DateTime, server_default=func.now())
    date_modified: any = Column(DateTime, server_default=func.now())


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


@dataclass
class ChildPlanning(Base):

    """ Planning Model for storing children plannings related details """

    __tablename__ = "children_plannings"

    uuid = Column(String, primary_key=True, unique=True)

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=False)
    child: Mapped[any] = relationship("Child", foreign_keys=child_uuid, uselist=False)

    day_uuid: str = Column(String, ForeignKey('days.uuid'), nullable=False)
    day: Mapped[any] = relationship("Day", foreign_keys=day_uuid, uselist=False)

    current_date: any = Column(Date, nullable=True)
    date_added: any = Column(DateTime, server_default=func.now())
    date_modified: any = Column(DateTime, server_default=func.now())