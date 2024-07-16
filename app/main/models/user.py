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

    email: str = Column(String, nullable=False, default="", index=True)
    firstname: str = Column(String(100), nullable=False, default="")
    lastname: str = Column(String(100), nullable=False, default="")

    avatar_uuid: str = Column(String, ForeignKey('storages.uuid'), nullable=True)
    avatar = relationship("Storage", foreign_keys=[avatar_uuid])

    role_uuid: str = Column(String, ForeignKey('roles.uuid'), nullable=False)
    role = relationship("Role", foreign_keys=[role_uuid],uselist = False)

    otp: str = Column(String(5), nullable=True, default="")
    otp_expired_at: datetime = Column(DateTime, nullable=True, default=None)

    otp_password: str = Column(String(5), nullable=True, default="")
    otp_password_expired_at: datetime = Column(DateTime, nullable=True, default=None)

    password_hash: str = Column(String(100), nullable=True, default="")
    status = Column(types.Enum(UserStatusType), index=True, nullable=False, default=UserStatusType.UNACTIVED)
    # status = Column(String, index=True, nullable=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<User: uuid: {} email: {}>'.format(self.uuid, self.email)


@event.listens_for(User, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(User, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


class UserActionValidation(Base):
    __tablename__ = 'user_action_validations'

    uuid: str = Column(String, primary_key=True)

    user_uuid: str = Column(String, ForeignKey('users.uuid'), nullable=True)
    code: str = Column(String, unique=False, nullable=True)
    expired_date: any = Column(DateTime, default=datetime.now())
    value: str = Column(String, default="", nullable=True)

    date_added: any = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(UserActionValidation, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()


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
