from pydantic import BaseModel,ConfigDict
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Enum

class NurseryCloseHourBase(BaseModel):
    name_fr: str
    name_en: str 
    start_day: int
    start_month: int
    end_day: int
    end_month: int
    nursery_uuid: str

class NurseryCloseHourCreate(NurseryCloseHourBase):
    pass

class NurseryCloseHourUpdate(BaseModel):
    name_fr: Optional[str] = None
    name_en: Optional[str] = None
    start_day: Optional[int] = None
    start_month: Optional[int] = None
    end_day: Optional[int] = None
    end_month: Optional[int] = None
    is_active: Optional[bool] = None
    
class NurseryCloseHour(NurseryCloseHourBase):
    uuid: str
    is_active: bool
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class NurseryCloseHourResponsiveList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page:int
    data: list[NurseryCloseHour]

    model_config = ConfigDict(from_attributes=True)

class NurseryCloseHourDetails(BaseModel):
    uuid : str
    name_fr: str
    name_en: str 
    start_day: int
    start_month: int
    end_day: int
    end_month: int

    model_config = ConfigDict(from_attributes=True)

class CopyParametersRequest(BaseModel):
    source_nursery_uuid: str
    target_nursery_uuid: str
    elements_to_copy: List[str]

    model_config = ConfigDict(from_attributes=True)
