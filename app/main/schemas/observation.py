from datetime import datetime
from typing import Any, Optional, List
from pydantic import BaseModel, ConfigDict

from app.main.schemas.preregistration import ChildMini2

from .nursery import NurserySlim
from .base import DataList


class ObservationBase(BaseModel):
    nursery_uuid: str
    child_uuids: list[str]
    employee_uuid: str
    observation: Optional[str] = None
    time: Optional[datetime] = None


class ObservationCreate(ObservationBase):
    pass

class ObservationUpdate(ObservationBase):
    uuid: Optional[str] = None

class Observation(BaseModel):
    uuid: Optional[str] = None
    child: Optional[ChildMini2] = None
    time: Optional[datetime] = None
    observation: Optional[str] = None
    nursery: Optional[NurserySlim]=None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class ObservationMini(BaseModel):
    uuid: Optional[str] = None
    time: Optional[datetime] = None
    observation: Optional[str] = None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)



class ObservationList(DataList):

    data: List[Observation] = []