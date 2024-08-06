from pydantic import BaseModel,ConfigDict
from datetime import datetime
from typing import List, Optional

from app.main.schemas.base import DataList


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