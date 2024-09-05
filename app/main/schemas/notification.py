from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from .base import DataList


class UnreadNotificationCount(BaseModel):
    user_id: Optional[str]

class MarkNotificationAsRead(BaseModel):
    notification_id: Optional[int]

class NotificationBase(BaseModel):
    type: Optional[str] = None
    user_uuid: Optional[str] = None
    payload_json: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(NotificationBase):
    pass

class Notification(BaseModel):
    uuid: Optional[str] = None
    is_read: Optional[bool] = False
    payload_json: Optional[dict] = None
    date_added: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SettingConfig(BaseModel):
    key: str
    mail_actived: bool = False
    push_actived: bool = False
    in_app_actived: bool = False

    model_config = ConfigDict(from_attributes=True)


class NotificationSettingSchema(BaseModel):
    uuid: str
    key: str
    title_fr: str
    title_en: str

    model_config = ConfigDict(from_attributes=True)

class NotificationSettingUpdate(BaseModel):
    pass


class NotificationSettingUserSchema(BaseModel):
    uuid: str
    mail_actived: bool
    push_actived: bool
    in_app_actived: bool
    notification_setting: NotificationSettingSchema

    model_config = ConfigDict(from_attributes=True)

class NotificationList(DataList):

    data: List[Notification] = []