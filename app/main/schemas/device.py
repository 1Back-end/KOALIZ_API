from datetime import datetime
from typing import Any, Optional, List
from pydantic import BaseModel, ConfigDict

from .file import File
from .base import DataList, Token



class DeviceBase(BaseModel):
    # player_id: Optional[str] = None
    # user_uuid: Optional[str] = None
    # token: Optional[str] = None
    name: Optional[str] = None
    # code: Optional[str] = None
    # qrcode_uuid: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DeviceCreate(DeviceBase):
    token: Optional[str] = None
    code: Optional[str] = None
    qrcode_uuid: Optional[str] = None


class DeviceUpdate(DeviceBase):
    pass

class Device(DeviceBase):
    uuid: Optional[str] = None
    # qrcode: Optional[File] = None
    date_added: datetime


class DeviceList(DataList):

    data: List[Device] = []

class DeviceAuthentication(BaseModel):
    device: Device
    token: Optional[Token] = None
    model_config = ConfigDict(from_attributes=True)