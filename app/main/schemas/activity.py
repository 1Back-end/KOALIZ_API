from pydantic import BaseModel,ConfigDict
from datetime import datetime
from typing import List, Optional

from app.main.schemas.base import DataList
from app.main.schemas.employee import EmployeSlim
from app.main.schemas.nursery import NurserySlim
from app.main.schemas.preregistration import ChildMini2


# ActivityCategory
class ActivityCategoryBase(BaseModel):
    name_fr: str
    name_en: str

class ActivityCategoryCreate(ActivityCategoryBase):
    pass

class ActivityCategoryUpdate(BaseModel):
    uuid: str
    name_fr: Optional[str] = None
    name_en: Optional[str] = None


class ActivityCategory(BaseModel):
    uuid: str
    name_fr: str
    name_en: str
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class ActivityCategoryList(DataList):

    data: List[ActivityCategory] = []

# Activity
class ActivityBase(BaseModel):
    name_fr: str
    name_en: str

class ActivityCreate(ActivityBase):
    pass

class ActivityUpdate(BaseModel):
    uuid: str
    name_fr: Optional[str] = None
    name_en: Optional[str] = None


class Activity(BaseModel):
    uuid: str
    name_fr: str
    name_en: str
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class ActivityList(DataList):

    data: List[Activity] = []


#  Child Activity
class ChildActivityBase(BaseModel):
    child_uuid: str
    activity_uuid: str
    nursery_uuid: str
    employee_uuid: str
    activity_time: datetime

class ChildActivityCreate(ChildActivityBase):
    pass

class ChildActivityUpdate(ChildActivityBase):
    pass


class ChildActivity(BaseModel):
    child: Optional[ChildMini2] = None
    nursery: Optional[NurserySlim]=None
    added_by: Optional[EmployeSlim] = None    
    activity: Activity
    activity_time: datetime
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class ChildActivityList(DataList):

    data: List[ChildActivity] = []
