from datetime import datetime
from typing import Any, Optional, List
from pydantic import BaseModel, ConfigDict

from app.main.models.children import MediaType
from app.main.schemas.file import File
from app.main.schemas.preregistration import ChildMini2

from .nursery import NurserySlim
from .base import DataList


class MediaBase(BaseModel):
    nursery_uuid: Optional[str] = None
    child_uuids: list[str] = None
    employee_uuid: Optional[str] = None
    observation: Optional[str] = None
    file_uuid: Optional[str] = None
    media_type: Optional[MediaType] = None
    time: Optional[datetime] = None


class MediaCreate(MediaBase):
    pass


class MediaUpdate(MediaBase):
    uuid: Optional[str] = None

class Media(BaseModel):
    uuid: Optional[str] = None
    children: list[ChildMini2] = None
    time: Optional[datetime] = None
    media_type: Optional[MediaType] = None
    file: Optional[File] = None
    observation: Optional[str] = None
    nursery: Optional[NurserySlim]=None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)
class MediaMini(BaseModel):
    uuid: Optional[str] = None
    time: Optional[datetime] = None
    media_type: Optional[MediaType] = None
    observation: Optional[str] = None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)



class MediaList(DataList):

    data: List[Media] = []