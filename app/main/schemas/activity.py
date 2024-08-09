from pydantic import BaseModel,ConfigDict
from datetime import datetime
from typing import List, Optional

from app.main.schemas.base import DataList

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

    