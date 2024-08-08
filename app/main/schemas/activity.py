from pydantic import BaseModel,ConfigDict
from datetime import datetime
from typing import List, Optional

from app.main.schemas.base import DataList
from app.main.schemas.employee import EmployeSlim
from app.main.schemas.nursery import NurserySlim
from app.main.schemas.preregistration import ChildMini2

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
    data: list[Optional[ActivityResponse]] =  []
