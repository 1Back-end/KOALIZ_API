from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from .user import AddedBy
from .base import DataList, Token
from .file import File

class MessageFileSend(BaseModel):
    receiver_uuid: str
    file_name: str
    file_uuid: str


class MessageBase(BaseModel):
    content: Optional[str] = None


class MessageCreate(MessageBase):
    pass


class MessageUpdate(MessageBase):
    pass

class Conversation(BaseModel):
    uuid: Optional[str] = None
    last_sender_uuid: Optional[str] = None
    last_message: Optional[str] = None
    is_read: bool = False
    sender: Optional[AddedBy]=None
    receiver: Optional[AddedBy]=None
    first_msg_date: datetime
    last_sending_date: datetime

    model_config = ConfigDict(from_attributes=True)

class Message(MessageBase):
    uuid: Optional[str] = None
    is_read: bool = False
    is_file: bool = False
    is_image: bool = False
    sender: Optional[AddedBy]=None
    file: Optional[File]=None
    sending_date: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationList(DataList):

    data: List[Conversation] = []

class MessageList(DataList):

    data: List[Message] = []

class MessageAuthentication(BaseModel):
    message: Message
    token: Optional[Token] = None
    model_config = ConfigDict(from_attributes=True)