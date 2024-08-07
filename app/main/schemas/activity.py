from pydantic import BaseModel,ConfigDict
from datetime import datetime
from typing import List, Optional

from app.main.schemas.base import DataList

class ActivityBase(BaseModel):
    uuid : str
    name_fr : str
    name_en : Optional[str]=None

class ActivityCreate(ActivityBase):
    pass

class ActivityUpdate(ActivityBase):
    uuid: str
    name_fr: Optional[str] = None
    name_en: Optional[str] = None

class ActivityResponse(BaseModel):
    uuid: str
    name_fr: str
    name_en: Optional[str] = None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)
    
class ActivityList(DataList):
    data: list[Optional[ActivityResponse]]

    model_config = ConfigDict(from_attributes=True)
