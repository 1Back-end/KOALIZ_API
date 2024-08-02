from datetime import datetime
from typing import Any, Optional, List
from pydantic import BaseModel, ConfigDict

from .nursery import NurserySlim
from .base import DataList, Token



class TeamDeviceBase(BaseModel):
    name: Optional[str] = None
    nursery_uuid: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TeamDeviceCreate(TeamDeviceBase):
    pass


class TeamDeviceUpdate(TeamDeviceBase):
    uuid: Optional[str] = None

class TeamDevice(TeamDeviceBase):
    uuid: Optional[str] = None
    # code: Optional[str] = None
    nursery: Optional[NurserySlim]=None
    date_added: datetime


class TeamDeviceList(DataList):

    data: List[TeamDevice] = []

class TeamDeviceAuthentication(BaseModel):
    token: Optional[Token] = None
    team_device: TeamDevice
    model_config = ConfigDict(from_attributes=True)