from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from .base import DataList
from app.main.models.tag import TagTypeEnum

class TagDelete(BaseModel):
    uuids:list[str]

class TagBase(BaseModel):
    title_fr:str
    title_en:str
    color:Optional[str] = None
    icon_uuid:Optional[str] = None
    type:Optional[TagTypeEnum]=None

class TagCreate(TagBase):
    title_fr:Optional[str] = None
    title_en:Optional[str] = None

    
class TagUpdate(TagBase):
    uuid:str
    title_fr:Optional[str] = None
    title_en:Optional[str] = None

class TagsInDB(TagBase):
    uuid:str
    date_added:datetime
    date_modified:datetime

    model_config = ConfigDict(from_attributes=True)

class Tag(TagsInDB):
    pass


class TagsResponseList(DataList):
    pass



