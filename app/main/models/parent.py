from dataclasses import dataclass
from app.main import models
from app.main.models.preregistration import ParentRelationship
from .user import UserStatusType
from sqlalchemy import Column, Float, ForeignKey, Integer, String, DateTime, Text, Table, Boolean,types,event
from datetime import datetime, date
from sqlalchemy.orm import relationship
from .db.base_class import Base


@dataclass
class Parent(Base):
    """
     database model for storing Parent related details
    """
    __tablename__ = 'parents'

    uuid: str = Column(String, primary_key=True, unique=True,index = True)

    firstname: str = Column(String(100), nullable=False, default="")
    lastname: str = Column(String(100), nullable=False, default="")
    email: str = Column(String, nullable=False, default="", index=True)
    link: str = Column(types.Enum(ParentRelationship), nullable=True)

    fix_phone: str = Column(String, nullable=True)
    phone: str = Column(String, nullable=True)

    recipient_number: str = Column(String, nullable=True)
    zip_code: str = Column(String, nullable=True)
    city: str = Column(String, nullable=True)
    country: str = Column(String, nullable=True)
    profession: str = Column(String, nullable=True)
    annual_income: float = Column(Float, default=0)
    company_name: str = Column(String, nullable = True)
    has_company_contract: bool = Column(Boolean, default=True)
    dependent_children: int = Column(Integer, default=0)
    disabled_children: int = Column(Integer, default=0)

    is_paying_parent: bool = Column(Boolean, default=False)

    role_uuid: str = Column(String, ForeignKey('roles.uuid',ondelete = "CASCADE",onupdate= "CASCADE"), nullable=False )
    role = relationship("Role", foreign_keys=[role_uuid],uselist = False)

    avatar_uuid: str = Column(String, ForeignKey('storages.uuid'), nullable=True)
    avatar = relationship("Storage", foreign_keys=[avatar_uuid])

    otp: str = Column(String(5), nullable=True, default="")
    otp_expired_at: datetime = Column(DateTime, nullable=True, default=None)

    otp_password: str = Column(String(5), nullable=True, default="")
    otp_password_expired_at: datetime = Column(DateTime, nullable=True, default=None)

    password_hash: str = Column(String(100), nullable=True, default="")
    status = Column(String, index=True, nullable=False)
    is_new_user: bool = Column(Boolean, nullable=True, default=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<Parent: uuid: {} email: {}>'.format(self.uuid, self.email)


@event.listens_for(Parent, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(Parent, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


class ParentActionValidation(Base):
    __tablename__ = 'parent_action_validations'

    uuid: str = Column(String, primary_key=True)

    user_uuid: str = Column(String, ForeignKey('parents.uuid'), nullable=True)
    code: str = Column(String, unique=False, nullable=True)
    expired_date: any = Column(DateTime, default=datetime.now())
    value: str = Column(String, default="", nullable=True)

    date_added: any = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(ParentActionValidation, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
