from pydantic import BaseModel, ConfigDict
from typing import Optional,Any
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
    element_uuid:str

    
class TagUpdate(TagBase):
    uuid:str
    title_fr:Optional[str] = None
    title_en:Optional[str] = None

class TagElement(BaseModel):
    uuid: str
    tag_uuid: str
    element_uuid: str
    element_type: str

    model_config = ConfigDict(from_attributes=True)


class TagsInDB(TagBase):
    uuid:str
    date_added:datetime
    date_modified:datetime
    tag_elements:list[TagElement]

    model_config = ConfigDict(from_attributes=True)

class Tag(TagsInDB):
    pass


class TagsResponseList(BaseModel):
    total: int
    pages: int
    current_page: int
    per_page: int
    data: list[Tag] = []



