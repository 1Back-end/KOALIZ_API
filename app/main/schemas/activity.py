from pydantic import BaseModel,ConfigDict
from datetime import datetime
from typing import Optional

class ActivityBase(BaseModel):
    activity_name_fr: str
    activity_name_en: str

    model_config = ConfigDict(from_attributes=True)

class ActivityCreate(ActivityBase):
    pass

class ActivityUpdateSchema(BaseModel):
    activity_name_fr: Optional[str] = None
    activity_name_en: Optional[str] = None
    activity_time: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ActivitySchema(BaseModel):
    uuid: str
    activity_name_fr: str
    activity_name_en: str
    activity_time: datetime
    date_added: datetime
    date_modified: datetime

    class Config:
        orm_mode: True
