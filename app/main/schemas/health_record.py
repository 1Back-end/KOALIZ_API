from datetime import datetime
from typing import Any, Optional, List
from pydantic import BaseModel, ConfigDict

from app.main.models.children import CareType, MedicationType, Route
from app.main.schemas.employee import EmployeSlim
from app.main.schemas.preregistration import ChildMini2

from .nursery import NurserySlim
from .base import DataList


class HealthRecordBase(BaseModel):
    nursery_uuid: Optional[str]
    child_uuid: Optional[str]
    employee_uuid: Optional[str]
    medication_name: Optional[str]
    observation: Optional[str]= None
    medication_type: Optional[MedicationType]= None
    care_type: Optional[CareType]= None
    route: Optional[Route]= None
    time: Optional[datetime]= None
    weight: Optional[float] = 0
    temperature: Optional[float] = 0


class HealthRecordCreate(HealthRecordBase):
    pass


class HealthRecordUpdate(HealthRecordBase):
    uuid: str

class HealthRecord(BaseModel):
    uuid: Optional[str] = None
    child: Optional[ChildMini2] = None
    nursery: Optional[NurserySlim]=None
    added_by: Optional[EmployeSlim] = None
    medication_name: Optional[str]
    observation: Optional[str]
    medication_type: Optional[str]= None
    care_type: Optional[CareType]= None
    route: Optional[Route]= None
    time: Optional[datetime]= None
    weight: Optional[float] = 0
    temperature: Optional[float] = 0
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class HealthRecordMini(BaseModel):
    uuid: Optional[str] = None
    medication_name: Optional[str]
    observation: Optional[str]
    medication_type: Optional[str]= None
    care_type: Optional[CareType]= None
    route: Optional[Route]= None
    time: Optional[datetime]= None
    weight: Optional[float] = 0
    temperature: Optional[float] = 0
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)


class HealthRecordList(DataList):

    data: List[HealthRecord] = []