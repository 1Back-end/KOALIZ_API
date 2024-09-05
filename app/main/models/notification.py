from enum import Enum
from dataclasses import dataclass
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import ForeignKey, event

from app.main.models.db.base_class import Base

from sqlalchemy import Column, String, DateTime, types, Boolean


class NotificationType(str, Enum):
    EVENT_NEW_NOTIFICATION = "EVENT_NEW_NOTIFICATION"
    EVENT_NEW_CONVERSATION = "EVENT_NEW_CONVERSATION"
    EVENT_NEW_MESSAGE_IN_CONVERSATION = "EVENT_NEW_MESSAGE_IN_CONVERSATION"
    RESET_PASSWORD = "RESET_PASSWORD"
    OPENING_MICRO_NURSERY = "OPENING_MICRO_NURSERY"
    REPORT_ABSENCE = "REPORT_ABSENCE"
    VACCINATION_REMINDER = "VACCINATION_REMINDER"
    REPORT_DELAY = "REPORT_DELAY"
    UNPAID_INVOICE_REMINDER = "UNPAID_INVOICE_REMINDER"
    NEW_MESSAGE = "NEW_MESSAGE"
    PREREGISTRATION_FOLDER = "PREREGISTRATION_FOLDER"
    CONTRACT_TERMINATION = "CONTRACT_TERMINATION"


@dataclass
class Notification(Base):

    __tablename__ = 'notifications'

    uuid: str = Column(String, primary_key=True, unique=True)
    type: str = Column(types.Enum(NotificationType), nullable=False, default=NotificationType.EVENT_NEW_NOTIFICATION)

    user_uuid: str = Column(String, nullable=False)

    payload_json: dict = Column(JSONB, nullable=False)
    is_read: bool = Column(Boolean, nullable=False, default=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@dataclass
class NotificationSettingUser(Base):

    """ Notification Setting User model for storing user notification settings related details """

    __tablename__ = "notification_setting_users"
    
    uuid = Column(String, primary_key=True, unique=True)

    mail_actived: bool = Column(Boolean, nullable=False, default=False) 
    push_actived: bool = Column(Boolean, nullable=False, default=False) 
    in_app_actived: bool = Column(Boolean, nullable=False, default=False) 

    user_uuid = Column(String(255), nullable=True)

    notification_setting_uuid = Column(String, ForeignKey('notifications_setting.uuid', ondelete="CASCADE"), nullable=True)
    notification_setting = relationship("NotificationSetting", foreign_keys=[notification_setting_uuid])

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<NotificationSettingUser: uuid: {} />'.format(self.uuid)

@dataclass
class NotificationSetting(Base):

    """ Notification Setting model for storing notification settings related details """

    __tablename__ = "notifications_setting"
    
    uuid = Column(String, primary_key=True, unique=True)

    key = Column(String, nullable=False, default="")
    title_en = Column(String, nullable=False, default="")
    title_fr = Column(String, nullable=False, default="")

    codes: dict = Column(JSONB, nullable=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<NotificationSetting: uuid: {} />'.format(self.uuid)
    
@dataclass
class Device(Base):
    __tablename__ = 'devices'

    uuid = Column(String, primary_key=True, unique=True)
    player_id = Column(String, default="", nullable=True)
    user_uuid = Column(String, nullable=True)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(Base, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the create/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(Base, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()
