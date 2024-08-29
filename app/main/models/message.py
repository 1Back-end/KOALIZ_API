from dataclasses import dataclass
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, String, DateTime, event, types
from sqlalchemy.sql.sqltypes import Boolean
from enum import Enum
from app.main import models
from app.main.models.db.session import SessionLocal
from .db.base_class import Base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import JSONB

class MessageType(str, Enum):
    RESERVATION = "RESERVATION"
    MESSAGE = "LITTLE_SLEEP"
    ABSENCE = "ABSENCE"
    LATE = "LATE"

class MessageStatusEnum(str,Enum):
    PROCESSED = "PROCESSED"
    DELETED = "DELETED"
    DELIVERED = "DELIVERED"

class ConversationStatusEnum(str,Enum):
    PENDING = "PENDING"
    DELETED = "DELETED"


@dataclass
class Message(Base):
    __tablename__ = 'messages'
    uuid = Column(String, primary_key=True, unique=True)
    conversation_uuid: str = Column(String, ForeignKey("conversations.uuid", ondelete='CASCADE'))
    content: str = Column(String, unique=False, nullable=False)
    message_type: str = Column(types.Enum(MessageType), nullable=True, default=MessageType.MESSAGE)
    is_read: bool = Column(Boolean, nullable=False, default=False)
    payload_json: dict = Column(JSONB, nullable=True)
    is_file: bool = Column(Boolean, nullable=True, default=False)
    is_image: bool = Column(Boolean, nullable=True, default=False)
    status:str = Column(String, index=True, nullable=True, default = "DELIVERED")
    sender_uuid: str = Column(String, nullable=False)
    file_uuid = Column(String(255), ForeignKey('storages.uuid', ondelete="CASCADE"), nullable=True)
    file = relationship("Storage", foreign_keys=[file_uuid])

    sending_date: any = Column('date_added', DateTime(timezone=True), default=datetime.now())

    @hybrid_property
    def sender(self):
        db = SessionLocal()
        user = db.query(models.Administrator).\
            filter(models.Administrator.uuid==self.sender_uuid,
                   models.Administrator.status.not_in([st.value for st in models.UserStatusType if  st.value == models.UserStatusType.ACTIVED])).\
                    first()
        if not user:
            user = db.query(models.Parent).\
                filter(models.Parent.uuid==self.sender_uuid,
                     models.Parent.status.not_in([st.value for st in models.UserStatusType if  st.value == models.UserStatusType.ACTIVED])).\
                        first()
        return user

    def __repr__(self):
        return '<Message: uuid: {} />'.format(self.uuid)

@event.listens_for(Message, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.sending_date = datetime.now()


@dataclass
class Conversation(Base):
    __tablename__ = 'conversations'
    uuid = Column(String, primary_key=True, unique=True)
    sender_uuid: str = Column(String, nullable=False)
    receiver_uuid: str = Column(String, nullable=False)

    last_sender_uuid: str = Column(String, nullable=False)
    last_message: str = Column(String, nullable=False)
    status:str = Column(String, index=True, nullable=True,default="PENDING")

    is_read: bool = Column(Boolean, nullable=False, default=False)
    first_msg_date: any = Column('date_added', DateTime(timezone=True), default=datetime.now())
    last_sending_date: any = Column('date_modified', DateTime(timezone=True), default=datetime.now(), onupdate=datetime.now)

    @hybrid_property
    def sender(self):
        db = SessionLocal()
        user = db.query(models.Administrator).\
            filter(models.Administrator.uuid==self.sender_uuid,
                   models.Administrator.status.not_in([st.value for st in models.UserStatusType if  st.value == models.UserStatusType.ACTIVED])).\
                    first()
        if not user:
            user = db.query(models.Parent).\
                filter(models.Parent.uuid==self.sender_uuid,
                     models.Parent.status.not_in([st.value for st in models.UserStatusType if  st.value == models.UserStatusType.ACTIVED])).\
                        first()
        return user

    @hybrid_property
    def receiver(self):
        db = SessionLocal()
        user = db.query(models.Administrator).\
            filter(models.Administrator.uuid==self.receiver_uuid,
                   models.Administrator.status.not_in([st.value for st in models.UserStatusType if  st.value == models.UserStatusType.ACTIVED])).\
                    first()
        if not user:
            user = db.query(models.Parent).\
                filter(models.Parent.uuid==self.receiver_uuid,
                     models.Parent.status.not_in([st.value for st in models.UserStatusType if  st.value == models.UserStatusType.ACTIVED])).\
                        first()
        return user

    def __repr__(self):
        return '<Conversation: uuid: {} />'.format(self.uuid)


@event.listens_for(Conversation, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.first_msg_date = datetime.now()
    target.last_sending_date = datetime.now()


@event.listens_for(Conversation, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.last_sending_date = datetime.now()