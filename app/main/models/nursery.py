from enum import Enum

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, desc, event, types,Text,Date,Boolean
from sqlalchemy.ext.hybrid  import hybrid_property
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
    # memberships = relationship("Membership",secondary="nursery_memberships",back_populates="nurseries",overlaps="nursery, memberships")
    memberships = relationship("NurseryMemberships", back_populates="nursery")
    address_uuid: str = Column(String, ForeignKey('addresses.uuid'), nullable=False)
    address = relationship("Address", foreign_keys=[address_uuid], uselist=False)

    status = Column(types.Enum(NurseryStatusType), index=True, nullable=False, default=NurseryStatusType.UNACTIVED)
    slug: str = Column(String, index=True, default="", unique=True, nullable=False)
    code: str = Column(String, default="")
    website: str = Column(String, default="")

    owner_uuid: str = Column(String, ForeignKey('owners.uuid'), nullable=False)
    owner = relationship("Owner", foreign_keys=[owner_uuid], uselist=False,back_populates="nurseries")

    employees = relationship("Employee",secondary="nursery_employees", back_populates="nurseries", overlaps="nursery,employee")

    added_by_uuid: str = Column(String, ForeignKey('administrators.uuid'), nullable=True)
    added_by = relationship("Administrator", foreign_keys=[added_by_uuid], uselist=False)

    is_actived: bool = Column(Boolean, default=False,nullable=True)  # Ajout de la colonne is_actived

    opening_hours = relationship("NurseryOpeningHour", back_populates="nursery", order_by="NurseryOpeningHour.day_of_week")

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    @hybrid_property
    def nb_memberships(self) -> int:
        return len(self.memberships ) if self.memberships else 0
    
    @hybrid_property
    def current_membership(self):
        from app.main.models import Membership,NurseryMemberships,MembershipEnum
        if self.memberships:
            for membership in self.memberships:
                if membership.status == MembershipEnum.ACTIVED:
                    return membership
        else:
            return None
    
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
    is_deleted: bool = Column(Boolean, default=False)


    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=False)
    nursery = relationship("Nursery", foreign_keys=[nursery_uuid], uselist=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


class NurseryCloseHour(Base):
    """
     database model for storing Nursery Close Hour related details
    """
    __tablename__ = "nursery_close_hours"
    
    uuid: str = Column(String, primary_key=True, index=True)
    name_fr: str = Column(String, nullable=True)
    name_en: str = Column(String, nullable=True)
    start_day: int = Column(Integer, nullable=False)
    start_month: int = Column(Integer, nullable=False)
    end_day: int = Column(Integer, nullable=False)
    end_month: int = Column(Integer, nullable=False)
    is_active: bool = Column(Boolean, default=False)  # Ajout de la colonne is_active
    is_deleted: bool = Column(Boolean, default=False)


    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=False)
    nursery = relationship("Nursery", foreign_keys=[nursery_uuid], uselist=False)


    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now)
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)



class NuseryHoliday(Base):
    __tablename__ = "nursery_holidays"
    
    uuid: str = Column(String, primary_key=True,index=True)
    name_fr: str = Column(String, nullable=True)
    name_en: str = Column(String, nullable=True)
    day: int = Column(Integer, nullable=True)
    month: int = Column(Integer, nullable=True)
    is_active: bool = Column(Boolean, default=False, nullable=False)  # Ajout de la colonne is_active
    is_deleted: bool = Column(Boolean, default=False)




    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=False)
    nursery = relationship("Nursery", foreign_keys=[nursery_uuid], uselist=False)


    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now)
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)




@event.listens_for(NurseryCloseHour, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(NurseryCloseHour, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()

@event.listens_for(NuseryHoliday, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(NuseryHoliday, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()

@event.listens_for(NurseryOpeningHour, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(NurseryOpeningHour, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()
