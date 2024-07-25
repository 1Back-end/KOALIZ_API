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

class Notification(NotificationBase):
    uuid: Optional[str] = None
    is_read: Optional[bool] = False
    date_added: datetime


class NotificationList(DataList):

    data: List[Notification] = []