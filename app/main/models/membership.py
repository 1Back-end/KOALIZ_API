from dataclasses import dataclass   
from .user import UserStatusType
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, Table, Boolean,types,event,Date,Float
from datetime import datetime, date
from sqlalchemy.orm import relationship,aliased
from .db.base_class import Base
from sqlalchemy.ext.hybrid import hybrid_property
from enum import Enum
from app.main.models.db.session import SessionLocal

class MembershipEnum(str,Enum):
    ACTIVED = "ACTIVED"
    UNACTIVED = "UNACTIVED"
    PENDING = "PENDING"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"


class MembershipType(str,Enum):
    """
    MembershipType Enum
    """
    DAY = "DAY"
    MONTH = "MONTH"
    YEAR = "YEAR"

# @dataclass
# class NurseryMemberships(Base):
#     """
#      database model for storing Membership and Nursery related details
#     """    
#     __tablename__ ='nursery_memberships'
#     uuid: str = Column(String, primary_key=True, unique=True,index = True)
#     nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid',ondelete = "CASCADE",onupdate= "CASCADE"), nullable=False )
#     membership_uuid: str = Column(String, ForeignKey('memberships.uuid',ondelete = "CASCADE",onupdate= "CASCADE"), nullable=False )
#     date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
#     date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

# @event.listens_for(NurseryMemberships, 'before_insert')
# def update_created_modified_on_create_listener(mapper, connection, target):
#     """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
#     target.date_added = datetime.now()
#     target.date_modified = datetime.now()


# @event.listens_for(NurseryMemberships, 'before_update')
# def update_modified_on_update_listener(mapper, connection, target):
#     """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
#     target.date_modified = datetime.now()

# @dataclass
# class MembershipType(Base):
#     """
#      database model for storing MembershipType related details
#     """
#     __tablename__ = 'membership_types'

#     uuid: str = Column(String, primary_key=True, unique=True,index = True)
#     title_fr: str = Column(String(100), unique=True, index=True)
#     title_en: str = Column(String(100), unique=True, index=True)
#     description: str = Column(Text)
#     date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
#     date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())
#     price: float = Column(Float, nullable=False, default=0.0)



    # def __repr__(self):
    #     return '<MembershipType: uuid: {} title_fr: {} title_en: {}>'.format(self.uuid, self.title_fr, self.title_en)

# @event.listens_for(MembershipType, 'before_insert')
# def update_created_modified_on_create_listener(mapper, connection, target):
#     """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
#     target.date_added = datetime.now()
#     target.date_modified = datetime.now()


# @event.listens_for(MembershipType, 'before_update')
# def update_modified_on_update_listener(mapper, connection, target):
#     """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
#     target.date_modified = datetime.now()

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
    
    # owner_uuid: str = Column(String, ForeignKey('owners.uuid',ondelete = "CASCADE",onupdate= "CASCADE"), nullable=False )
    # owner = relationship("Owner", foreign_keys=[owner_uuid],uselist = False)

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid',ondelete = "CASCADE",onupdate= "CASCADE"), nullable=False )
    nursery = relationship("Nursery", foreign_keys=[nursery_uuid],back_populates="memberships")

    period_from:datetime = Column(DateTime, nullable=False, default=datetime.utcnow())
    period_to: datetime = Column(DateTime, nullable=False, default=datetime.utcnow())
    period_unit:str = Column(types.Enum(MembershipType), index=True, nullable=False) #DAY,
    
    duration:float = Column(Float, nullable=False)
     
    status:str = Column(types.Enum(MembershipEnum), index=True, nullable=False, default = MembershipEnum.PENDING)
    date_added: datetime = Column(DateTime, nullable=False, default=datetime.utcnow())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.utcnow())

    def __repr__(self):
        return '<Membership: uuid: {} period_from: {} period_to: {} status: {} >'.format(self.uuid, self.period_from, self.period_to,self.status)

@event.listens_for(Membership, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.utcnow()
    target.date_modified = datetime.utcnow()


@event.listens_for(Membership, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.utcnow()