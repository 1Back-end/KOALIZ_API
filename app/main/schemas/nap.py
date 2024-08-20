from datetime import datetime
from typing import Any, Optional, List
from pydantic import BaseModel, ConfigDict

from app.main.models.children import NapQuality
from app.main.schemas.preregistration import ChildMini2

from .nursery import NurserySlim
from .base import DataList


class NapBase(BaseModel):
    nursery_uuid: Optional[str] = None
    child_uuid_tab: Optional[list[str]]
    employee_uuid: Optional[str] = None
    observation: Optional[str] = None
    quality: Optional[NapQuality] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class NapCreate(NapBase):
    pass


class NapUpdate(NapBase):
    uuid: str

class Nap(BaseModel):
    uuid: Optional[str] = None
    child: Optional[ChildMini2] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    quality: Optional[NapQuality] = None
    observation: Optional[str] = None
    duration: Optional[int] = 0
    nursery: Optional[NurserySlim]=None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)
class NapMini(BaseModel):
    uuid: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    quality: Optional[NapQuality] = None
    observation: Optional[str] = None
    duration: Optional[int] = 0
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)



class NapList(DataList):

    data: List[Nap] = []