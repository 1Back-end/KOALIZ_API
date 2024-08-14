from datetime import datetime
from typing import Any, Optional, List
from pydantic import BaseModel, ConfigDict

from app.main.models.children import AdditionalCare, Cleanliness, StoolType
from app.main.schemas.employee import EmployeSlim
from app.main.schemas.preregistration import ChildMini2

from .nursery import NurserySlim
from .base import DataList


class HygieneChangeBase(BaseModel):
    nursery_uuid: str
    child_uuids: list[str]
    employee_uuid: str
    time: Optional[datetime]= None
    cleanliness: Optional[Cleanliness]= None
    pipi: Optional[bool] = False
    stool_type: Optional[StoolType]= None
    additional_care: Optional[AdditionalCare]= None
    observation: Optional[str]= None


class HygieneChangeCreate(HygieneChangeBase):
    pass


class HygieneChangeUpdate(HygieneChangeBase):
    uuid: Optional[str] = None

class HygieneChange(BaseModel):
    uuid: Optional[str] = None
    child: Optional[ChildMini2] = None
    nursery: Optional[NurserySlim]=None
    added_by: Optional[EmployeSlim]
    time: Optional[datetime]= None
    cleanliness: Optional[Cleanliness]= None
    pipi: Optional[bool] = False
    stool_type: Optional[StoolType]= None
    additional_care: Optional[AdditionalCare]= None
    observation: Optional[str]= None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class HygieneChangeMini(BaseModel):
    uuid: Optional[str] = None
    time: Optional[datetime]= None
    cleanliness: Optional[Cleanliness]= None
    pipi: Optional[bool] = False
    stool_type: Optional[StoolType]= None
    additional_care: Optional[AdditionalCare]= None
    observation: Optional[str]= None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)


class HygieneChangeList(DataList):

    data: List[HygieneChange] = []