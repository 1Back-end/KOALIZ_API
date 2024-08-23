from dataclasses import dataclass   
from .user import UserStatusType
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, Table, Boolean,types,event,Date,Float
from datetime import datetime, date
from sqlalchemy.orm import relationship,aliased,joinedload
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


@dataclass
class NurseryMemberships(Base):
    """
     database model for storing Membership and Nursery related details.
    """    
    __tablename__ ='nursery_memberships'
    uuid: str = Column(String, primary_key=True, unique=True,index = True)
    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid',ondelete = "CASCADE",onupdate= "CASCADE"), nullable=False )
    
    nursery =relationship("Nursery",foreign_keys=[nursery_uuid],uselist=False)
    # nurseries = relationship("Nursery",foreign_keys=[nursery_uuid],secondary="nurseries",backref='memberships',overlaps='memberships')
    
    membership_uuid: str = Column(String, ForeignKey('memberships.uuid',ondelete = "CASCADE",onupdate= "CASCADE"), nullable=False )
    
    memberships = relationship("Membership",foreign_keys=[membership_uuid],uselist= False)
    
    period_from:datetime = Column(DateTime, nullable=False, default=datetime.utcnow())
    period_to: datetime = Column(DateTime, nullable=False, default=datetime.utcnow())
    period_unit:str = Column(String(10), nullable=False)
    duration:float = Column(Float, nullable=False)
     
    status:str = Column(types.Enum(MembershipEnum), index=True, nullable=False, default = MembershipEnum.PENDING)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    @hybrid_property
    def membership_type(self):
        return self.memberships

@event.listens_for(NurseryMemberships, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(NurseryMemberships, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()

@dataclass
class Membership(Base):
    """
     database model for storing Membership related details
    """
    __tablename__ = 'memberships'

    uuid: str = Column(String, primary_key=True, unique=True,index = True)

    title_fr: str = Column(String(100), index=True)
    title_en: str = Column(String(100), index=True)
    description: str = Column(Text)
    # nurseries = relationship("Nursery", secondary="nursery_memberships", back_populates="memberships",overlaps="memberships, nursery")
    nurseries = relationship("NurseryMemberships", back_populates="memberships")
    date_added: datetime = Column(DateTime, nullable=False, default=datetime.utcnow())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.utcnow())


    def __repr__(self):
        return '<Membership: uuid: {} title_fr: {} title_en: {} description: {} >'.format(self.uuid, self.title_fr, self.title_en,self.description)

@event.listens_for(Membership, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.utcnow()
    target.date_modified = datetime.utcnow()


@event.listens_for(Membership, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.utcnow()