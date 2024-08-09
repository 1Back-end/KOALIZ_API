from datetime import datetime, date
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
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class OccasionalPresenceCreate(OccasionalPresenceBase):
    pass


class OccasionalPresenceUpdate(OccasionalPresenceBase):
    uuid: Optional[str] = None

class OccasionalPresence(BaseModel):
    uuid: Optional[str] = None
    child: Optional[ChildMini2] = None
    date: date
    note: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    nursery: Optional[NurserySlim]=None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)
class OccasionalPresenceMini(BaseModel):
    uuid: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    date: date
    note: Optional[str] = None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)


class OccasionalPresenceList(DataList):

    data: List[OccasionalPresence] = []