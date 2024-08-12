from datetime import datetime, date
from typing import Any, Optional, List
from pydantic import BaseModel, ConfigDict

# from app.main.schemas.preregistration import ChildMini2

from .nursery import NurserySlim
from .base import DataList


class AttendanceBase(BaseModel):
    nursery_uuid: str
    child_uuid: str
    employee_uuid: str
    date: date
    arrival_time: Optional[datetime] = None
    departure_time: Optional[datetime] = None


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(AttendanceBase):
    uuid: Optional[str] = None

class Attendance(BaseModel):
    uuid: Optional[str] = None
    # child: Optional[ChildMini2] = None
    nursery: Optional[NurserySlim]=None
    arrival_time: Optional[datetime] = None
    departure_time: Optional[datetime] = None
    date: date
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class AttendanceMini(BaseModel):
    uuid: Optional[str] = None
    arrival_time: Optional[datetime] = None
    departure_time: Optional[datetime] = None
    date: date
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class AttendanceList(DataList):

    data: List[Attendance] = []