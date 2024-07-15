from dataclasses import dataclass   
from .user import UserStatusType
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, Table, Boolean,types,event
from datetime import datetime, date
from sqlalchemy.orm import relationship
from .db.base_class import Base




@dataclass
class Role(Base):
    """
    Database model for storing Role related details
    """
    __tablename__ = 'roles'

    uuid: str = Column(String, primary_key=True, unique=True,index = True)
    group: str = Column(String(10), unique=True,index = True)
    code: str = Column(String(10), unique=True,index = True)
    title_fr: str = Column(String(100), unique=True, index=True)
    title_en: str = Column(String(100), unique=True, index=True)
    group: str = Column(String(100), index=True,nullable=False)
    description: str = Column(Text)
    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<Role: uuid: {} title_fr: {} title_en: {} code: {} group: {}>'.format(self.uuid, self.title_fr, self.title_en,self.code,self.group)
    
@event.listens_for(Role, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(Role, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()
