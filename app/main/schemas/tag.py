from pydantic import BaseModel, ConfigDict
from typing import Optional,Any
from datetime import datetime
from .base import DataList
from app.main.models.tag import TagTypeEnum

class   TagElementCreate(BaseModel):
    tag_uuids: list[str]
    element_uuid: str
    element_type: TagTypeEnum

class TagDelete(BaseModel):
    uuids:list[str]

class TagElementDelete(TagDelete):
    pass


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

class TagElementUpdate(BaseModel):
    uuid: str
    tag_uuid: Optional[str] = None
    element_uuid: Optional[str] = None
    element_type: Optional[TagTypeEnum]

class TagElement(BaseModel):
    uuid: str
    tag_uuid: str
    element_uuid: str
    element_type: str
    element:Optional[Any] = None

    model_config = ConfigDict(from_attributes=True)


class TagElementResponseList(BaseModel):
    total: int
    pages: int
    current_page: int
    per_page: int
    data: list[TagElement] = []
    
class TagsInDB(TagBase):
    uuid:str
    date_added:datetime
    date_modified:datetime
    tag_elements:list[TagElement]

    model_config = ConfigDict(from_attributes=True)

class Tag(TagsInDB):
    model_config = ConfigDict(from_attributes=True)



class TagsResponseList(BaseModel):
    total: int
    pages: int
    current_page: int
    per_page: int
    data: list[Tag] = []



