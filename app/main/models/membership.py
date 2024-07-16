from dataclasses import dataclass   
from .user import UserStatusType
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, Table, Boolean,types,event,Date,Float
from datetime import datetime, date
from sqlalchemy.orm import relationship
from .db.base_class import Base
from enum import Enum

class MembershipEnum(str,Enum):
    ACTIVED = "ACTIVED"
    UNACTIVED = "UNACTIVED"
    PENDING = "PENDING"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"


@dataclass
class MembershipType(Base):
    """
     database model for storing MembershipType related details
    """
    __tablename__ = 'membership_types'

    uuid: str = Column(String, primary_key=True, unique=True,index = True)
    title_fr: str = Column(String(100), unique=True, index=True)
    title_en: str = Column(String(100), unique=True, index=True)
    description: str = Column(Text)
    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())
    price: float = Column(Float, nullable=False, default=0.0)

    def __repr__(self):
        return '<MembershipType: uuid: {} title_fr: {} title_en: {}>'.format(self.uuid, self.title_fr, self.title_en)

@dataclass
class Membership(Base):
    """
     database model for storing Membership related details
    """
    __tablename__ = 'memberships'

    uuid: str = Column(String, primary_key=True, unique=True,index = True)
    title_fr: str = Column(String(100), unique=True, index=True)
    title_en: str = Column(String(100), unique=True, index=True)
    description: str = Column(Text)
    
    owner_uuid: str = Column(String, ForeignKey('owners.uuid',ondelete = "CASCADE",onupdate= "CASCADE"), nullable=False )
    owner = relationship("Owner", foreign_keys=[owner_uuid],uselist = False)

    period_from:datetime = Column(DateTime, nullable=False, default=datetime.now())
    period_to: datetime = Column(DateTime, nullable=False, default=datetime.now())

    price: float = Column(Float, nullable=False, default=0.0)

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid',ondelete = "CASCADE",onupdate= "CASCADE"), nullable=False )
    nurseries = relationship("Nursery", foreign_keys=[nursery_uuid])
    
    membership_type_uuid: str = Column(String, ForeignKey('membership_types.uuid',ondelete = "CASCADE",onupdate= "CASCADE"), nullable=False )
    membership_type = relationship("MembershipType", foreign_keys=[membership_type_uuid],uselist = False)

    status = Column(types.Enum(UserStatusType), index=True, nullable=False, default=UserStatusType.UNACTIVED)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<Membership: uuid: {} period_from: {} period_to: {} status: {} price: {}>'.format(self.uuid, self.period_from, self.period_to,self.status,self.price)

@event.listens_for(Membership, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(Membership, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()