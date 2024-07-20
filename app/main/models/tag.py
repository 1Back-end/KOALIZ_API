from enum import Enum
from dataclasses import dataclass
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, event, types
from datetime import datetime, date
from sqlalchemy.orm import relationship
from .db.base_class import Base


class TagTypeEnum(str, Enum):
    CHILDREN = "CHILDREN"
    CUSTOMER_ACCOUNT = "CUSTOMER_ACCOUNT"
    TEAM = "TEAM"
    PARENTS = "PARENTS"
    DOCUMENTS = "DOCUMENTS"
    PRE_ENROLLMENT = "PRE_ENROLLMENT"
    PICTURE = "PICTURE"
    BILL = "BILL"


@dataclass
class Tags(Base):
    """
     database model for storing Tags related details
    """
    __tablename__ = 'tags'

    uuid: str = Column(String, primary_key=True, unique=True, index=True)
    title_fr: str = Column(String(100), unique=True, index=True)
    title_en: str = Column(String(100), unique=True, index=True)

    color: str = Column(String, nullable=True)
    icon_uuid: str = Column(String, ForeignKey('storages.uuid'), nullable=True)
    icon = relationship("Storage", foreign_keys=[icon_uuid], uselist=False)

    type:str = Column(types.Enum(TagTypeEnum), index=True, nullable=True)

    # added_by_uuid: str = Column(String, ForeignKey('administrators.uuid'), nullable=True)
    # added_by = relationship("Administrator", foreign_keys=[added_by_uuid], uselist=False)


    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<Tags: uuid: {} title_fr: {} title_en {}>'.format(self.uuid, self.title_fr, self.title_en)


@event.listens_for(Tags, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(Tags, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()