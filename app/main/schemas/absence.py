from datetime import datetime
from typing import Any, Optional, List
from pydantic import BaseModel, ConfigDict

from app.main.schemas.preregistration import ChildMini2

from .nursery import NurserySlim
from .base import DataList


class AbsenceBase(BaseModel):
    nursery_uuid: str
    child_uuid_tab: list[str]
    employee_uuid: str
    note: Optional[str] = None
    start_time: datetime
    end_time: datetime


class AbsenceCreate(AbsenceBase):
    pass
    
class AbsenceUpdate(AbsenceBase):
    uuid: str


class Absence(BaseModel):
    uuid: str 
    child: Optional[ChildMini2] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    note: Optional[str] = None
    nursery: Optional[NurserySlim]=None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class AbsenceMini(BaseModel):
    uuid: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    note: Optional[str] = None
    duration: Optional[int] = 0
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)


class AbsenceList(DataList):

    data: List[Absence] = []