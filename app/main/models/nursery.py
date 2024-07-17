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
    # memberships = relationship("Membership",secondary="nursery_memberships",back_populates="nurseries")

    address_uuid: str = Column(String, ForeignKey('addresses.uuid'), nullable=False)
    address = relationship("Address", foreign_keys=[address_uuid], uselist=False)

    status = Column(types.Enum(NurseryStatusType), index=True, nullable=False, default=NurseryStatusType.ACTIVED)

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
