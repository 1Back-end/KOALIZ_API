from enum import Enum

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, event, types
from datetime import datetime, date
from sqlalchemy.orm import relationship
from .db.base_class import Base


class NurseryStatusType(str, Enum):
    ACTIVED = "ACTIVED"
    UNACTIVED = "UNACTIVED"
    DELETED = "DELETED"


class Nursery(Base):
    """
     database model for storing Nursery related details
    """
    __tablename__ = 'nurseries'

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    email: str = Column(String, nullable=False, default="", index=True)
    name: str = Column(String, nullable=False, default="")

    logo_uuid: str = Column(String, ForeignKey('storages.uuid'), nullable=True)
    logo = relationship("Storage", foreign_keys=[logo_uuid], uselist=False)

    signature_uuid: str = Column(String, ForeignKey('storages.uuid'), nullable=True)
    signature = relationship("Storage", foreign_keys=[signature_uuid], uselist=False)

    stamp_uuid: str = Column(String, ForeignKey('storages.uuid'), nullable=True)
    stamp = relationship("Storage", foreign_keys=[stamp_uuid], uselist=False)

    total_places: int = Column(Integer, default=0)
    phone_number: str = Column(String, nullable=False, default="")
    memberships = relationship("Membership",secondary="nursery_memberships",back_populates="nurseries",overlaps="nursery, memberships")
    
    address_uuid: str = Column(String, ForeignKey('addresses.uuid'), nullable=False)
    address = relationship("Address", foreign_keys=[address_uuid], uselist=False)

    status = Column(types.Enum(NurseryStatusType), index=True, nullable=False, default=NurseryStatusType.ACTIVED)
    slug: str = Column(String, index=True, default="", unique=True, nullable=False)
    website: str = Column(String, default="")

    owner_uuid: str = Column(String, ForeignKey('owners.uuid'), nullable=False)
    owner = relationship("Owner", foreign_keys=[owner_uuid], uselist=False)

    # memberships= relationship("NurseryMemberships",secondary="nursery_memberships",back_populates="nursery",overlaps="memberships")

    added_by_uuid: str = Column(String, ForeignKey('administrators.uuid'), nullable=True)
    added_by = relationship("Administrator", foreign_keys=[added_by_uuid], uselist=False)

    opening_hours = relationship("NurseryOpeningHour", back_populates="nursery", order_by="NurseryOpeningHour.day_of_week")

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<Nursery: uuid: {} email: {}>'.format(self.uuid, self.email)


@event.listens_for(Nursery, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(Nursery, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


class NurseryOpeningHour(Base):
    """
     database model for storing Nursery Opening Hour related details
    """
    __tablename__ = "nursery_opening_hours"

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    day_of_week: int = Column(Integer, nullable=False)
    from_time: str = Column(String(5), nullable=False)
    to_time: str = Column(String(5), nullable=False)

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=False)
    nursery = relationship("Nursery", foreign_keys=[nursery_uuid], uselist=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(NurseryOpeningHour, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(NurseryOpeningHour, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()
