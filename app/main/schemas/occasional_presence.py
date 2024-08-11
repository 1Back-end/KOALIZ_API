from datetime import datetime, date, time
from typing import Any, Optional, List
from pydantic import BaseModel, ConfigDict

from app.main.schemas.preregistration import ChildMini2

from .nursery import NurserySlim
from .base import DataList


class OccasionalPresenceBase(BaseModel):
    nursery_uuid: Optional[str] = None
    child_uuid: Optional[str] = None
    employee_uuid: Optional[str] = None
    date: date
    note: Optional[str] = None
    start_time: datetime = None
    end_time: datetime = None


class OccasionalPresenceCreate(OccasionalPresenceBase):
    pass


class OccasionalPresenceUpdate(OccasionalPresenceBase):
    uuid: str 

class OccasionalPresence(BaseModel):
    uuid: Optional[str] = None
    child: Optional[ChildMini2] = None
    date: date
    note: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    nursery: Optional[NurserySlim]=None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)
class OccasionalPresenceMini(BaseModel):
    uuid: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    date: date
    note: Optional[str] = None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)


class OccasionalPresenceList(DataList):

    data: List[OccasionalPresence] = []