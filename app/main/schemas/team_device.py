from datetime import datetime
from typing import Any, Optional,List
from pydantic import BaseModel, ConfigDict

from .nursery import NurserySlim
from .base import DataList, Token
from . employee import EmployeSlim


class TeamDeviceBase(BaseModel):
    name: Optional[str] = None
    nursery_uuid: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TeamDeviceCreate(TeamDeviceBase):
    pass


class TeamDeviceUpdate(TeamDeviceBase):
    uuid: Optional[str] = None

class Member(EmployeSlim):
    pass

class TeamDevice(TeamDeviceBase):
    uuid: Optional[str] = None
    code: Optional[str] = None
    nursery: Optional[NurserySlim]=None
    date_added: datetime

class TeamDeviceSlim(TeamDevice):
    members: Optional[list[Member]] = None



class TeamDeviceList(DataList):

    data: List[TeamDevice] = []

class TeamDeviceAuthentication(BaseModel):
    token: Optional[Token] = None
    team_device: Optional[TeamDeviceSlim] = None
    model_config = ConfigDict(from_attributes=True)