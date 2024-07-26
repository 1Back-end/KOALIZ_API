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


@dataclass
class Notification(Base):

    __tablename__ = 'notifications'

    uuid: str = Column(String, primary_key=True, unique=True)
    type: str = Column(types.Enum(NotificationType), nullable=False, default=NotificationType.EVENT_NEW_NOTIFICATION)

    user_uuid: str = Column(String, nullable=False)

    payload_json: dict = Column(JSONB, nullable=False)
    is_read: bool = Column(Boolean, nullable=False, default=False)

    date_added: any = Column(DateTime, server_default=func.now())
    date_modified: any = Column(DateTime, server_default=func.now(), onupdate=func.now())


@event.listens_for(Notification, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the create/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(Notification, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()
