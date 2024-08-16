from dataclasses import dataclass
from sqlalchemy import Boolean, Column, ForeignKey, String, DateTime,event
from datetime import datetime
from .db.base_class import Base
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.ext.hybrid import hybrid_property

@dataclass
class TeamDevice(Base):
    __tablename__ = 'team_devices'

    uuid = Column(String, primary_key=True, unique=True)
    token = Column(String, nullable=True)
    name = Column(String, nullable=True)
    code = Column(String, nullable=True)
    is_actived: bool = Column(Boolean, default=False, nullable=True)

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    @hybrid_property
    def members(self):
        employees = self.nursery.employees
        active_employees = [employee for employee in employees if employee.status != "DELETED"]
        return active_employees if active_employees else []
    
    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(TeamDevice, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is added, and sets the create/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(TeamDevice, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()
