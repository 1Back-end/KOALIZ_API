from dataclasses import dataclass
from enum import Enum
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, Table, Boolean,types,event
from datetime import datetime, date
from sqlalchemy.orm import relationship
from .db.base_class import Base


class UserStatusType(str, Enum):
    ACTIVED = "ACTIVED"
    UNACTIVED = "UNACTIVED"
    DELETED = "DELETED"
    BLOCKED = "BLOCKED"


@dataclass
class User(Base):
    """
    User model for storing users related details
    """
    __tablename__ = 'users'

    uuid: str = Column(String, primary_key=True, unique=True)

    country_code: str = Column(String(5), nullable=False, default="", index=True)
    phone_number: str = Column(String(20), nullable=False, default="", index=True)
    full_phone_number: str = Column(String(25), nullable=False, default="", index=True)
    first_name: str = Column(String(100), nullable=False, default="")
    last_name: str = Column(String(100), nullable=False, default="")
    email: str = Column(String(100), nullable=False, default="", index=True)
    address: str = Column(String(100), nullable=False, default="")
    birthday: date = Column(DateTime, nullable=True, default=None)
    storage_uuid: str = Column(String(100), nullable=True)

    otp: str = Column(String(5), nullable=True, default="")
    otp_expired_at: datetime = Column(DateTime, nullable=True, default=None)

    otp_password: str = Column(String(5), nullable=True, default="")
    otp_password_expired_at: datetime = Column(DateTime, nullable=True, default=None)

    password_hash: str = Column(String(100), nullable=True, default="")
    status = Column(types.Enum(UserStatusType), index=True, nullable=False, default=UserStatusType.UNACTIVED)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<User: uuid: {} full_phone_number: {}>'.format(self.uuid, self.full_phone_number)


@event.listens_for(User, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(User, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


@dataclass
class Device(Base):
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True)
    player_id = Column(String, default="", nullable=True)
    user_uuid = Column(String)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(Device, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is added, and sets the create/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(Device, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()
