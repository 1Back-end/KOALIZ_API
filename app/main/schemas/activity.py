from pydantic import BaseModel,ConfigDict
from datetime import datetime
from typing import List, Optional

from app.main.schemas.base import DataList
# from app.main.schemas.employee import EmployeSlim
# from app.main.schemas.nursery import NurserySlim
# from app.main.schemas.preregistration import ChildMini2

# ActivityCategory
class ActivityCategoryBase(BaseModel):
    name_fr: str
    name_en: str

class ActivityCategoryCreate(ActivityCategoryBase):
    activity_type_uuid_tab:Optional[list[str]]

class ActivityCategoryUpdate(BaseModel):
    uuid: str
    activity_type_uuid_tab:Optional[list[str]]
    name_fr: Optional[str] = None
    name_en: Optional[str] = None

class ActivityCategoryDelete(BaseModel):
    uuid: str
    activity_type_uuid_tab: Optional[list[str]]

class ActivityMini(BaseModel):
    uuid: str
    name_fr: str
    name_en: Optional[str] = None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class ActivityCategory(BaseModel):
    uuid: str
    name_fr: str
    name_en: str
    activities: list[ActivityMini]
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class ActivityCategoryList(DataList):

    data: List[ActivityCategory] = []

# Activity



class ActivityBase(BaseModel):
    name_fr : str
    name_en : str

class ActivityCreate(ActivityBase):
    activity_category_uuid_tab:list[str]


class ActivityUpdate(ActivityBase):
    uuid: str
    activity_category_uuid_tab: Optional[List[str]] = None
    name_fr: Optional[str] = None
    name_en: Optional[str] = None



class ActivityResponse(BaseModel):
    uuid: str
    name_fr: str
    name_en: str
    activity_categories:list[ActivityMini]
    date_added: datetime
    date_modified: datetime


    model_config = ConfigDict(from_attributes=True)
    
class ActivityList(DataList):
    data: List[ActivityResponse] = []

    model_config = ConfigDict(from_attributes=True)

# Child Activity
class ChildActivityBase(BaseModel):
    child_uuids : list[str]
    activity_uuid : str
    nursery_uuid : str
    employee_uuid: str
    activity_time: datetime

class ChildActivityCreate(ChildActivityBase):
    pass

class ChildActivityUpdate(BaseModel):
    child_uuid: str
    activity_uuid : str
    activity_time: datetime

class ChildActivityDelete(BaseModel):
    child_uuid: str
    activity_uuid : str


class ChildActivityDetails(BaseModel):
    activity_time: datetime
    # child: Optional[ChildMini2] = None
    # nursery: Optional[NurserySlim]=None
    # added_by: Optional[EmployeSlim] = None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)
    
class ChildActivityList(DataList):
    data: list[Optional[ChildActivityDetails]]

    model_config = ConfigDict(from_attributes=True)
    
