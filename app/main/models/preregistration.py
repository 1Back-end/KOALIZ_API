from enum import Enum

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, event, types, Date, ARRAY, Float, Boolean
from datetime import datetime, date

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship, Mapped
from .db.base_class import Base


class PreRegistrationStatusType(str, Enum):
    ACCEPTED = "ACCEPTED"
    PENDING = "PENDING"
    REFUSED = "REFUSED"


class Gender(str, Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    OTHER = 'OTHER'
    NOT_GIVEN = 'NOT_GIVEN'


class ParentRelationship(str, Enum):
    MOTHER = "MOTHER"
    FATHER = "FATHER"
    SISTER = "SISTER"
    BROTHER = "BROTHER"
    AUNT = "AUNT"
    UNCLE = "UNCLE"
    STEPMOTHER = "STEPMOTHER"
    STEPFATHER = "STEPFATHER"
    GRANDMOTHER = "GRANDMOTHER"
    GRANDFATHER = "GRANDFATHER"
    TUTORF = "TUTORF"
    TUTORM = "TUTORM"
    OTHER = "OTHER"


class Child(Base):
    """
         database model for storing Nursery related details
    """
    __tablename__ = 'children'

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    firstname: str = Column(String, nullable=False)
    lastname: str = Column(String, nullable=False)
    gender: str = Column(types.Enum(Gender), nullable=False, default=Gender.NOT_GIVEN)
    birthdate: date = Column(Date, nullable=False)
    birthplace: str = Column(String)

    contract_uuid: str = Column(String, ForeignKey('contracts.uuid'), nullable=True)
    contract: Mapped[any] = relationship("Contract", foreign_keys=contract_uuid, back_populates="child", uselist=False)

    parents: Mapped[list[any]] = relationship("ParentGuest", back_populates="child", uselist=True)

    preregistrations: Mapped[list[any]] = relationship("PreRegistration", back_populates="child", uselist=True)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

@event.listens_for(Child, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(Child, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


class Contract(Base):
    """
         database model for storing Nursery Opening Hour related details
    """
    __tablename__ = "contracts"

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    begin_date: date = Column(Date, nullable=False)
    end_date: date = Column(Date, nullable=False)
    # typical_weeks: list = relationship("TypicalWeek", backref="contract")
    # typical_weeks: Mapped[list[any]] = relationship("TypicalWeek", back_populates="contract", uselist=True)
    # typical_weeks: list[any] = Column(MutableList.as_mutable(ARRAY(JSONB)), nullable=False)
    typical_weeks: list[any] = Column(MutableList.as_mutable(JSONB), nullable=False)
    child: Mapped[any] = relationship("Child", back_populates="contract", uselist=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(Contract, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(Contract, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


class ParentGuest(Base):
    """
         database model for storing Nursery Opening Hour related details
    """
    __tablename__ = "parent_guests"

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    link: str = Column(types.Enum(ParentRelationship), nullable=False)
    firstname: str = Column(String, nullable=False)
    lastname: str = Column(String, nullable=False)
    birthplace: str = Column(String)
    fix_phone: str = Column(String, nullable=False)
    phone: str = Column(String, nullable=False)
    email: str = Column(String, nullable=False)
    recipient_number: str = Column(String, nullable=False)
    zip_code: str = Column(String, nullable=False)
    city: str = Column(String, nullable=False)
    country: str = Column(String, nullable=False)
    profession: str = Column(String, nullable=False)
    annual_income: float = Column(Float, default=0)
    company_name: str = Column(String, default=0)
    has_company_contract: bool = Column(Boolean, default=True)
    dependent_children: int = Column(Integer, default=0)
    disabled_children: int = Column(Integer, default=0)

    child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=True)
    child: Mapped[any] = relationship("Child", foreign_keys=child_uuid, back_populates="parents", uselist=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

@event.listens_for(ParentGuest, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(ParentGuest, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()




class PreRegistration(Base):
    """
     database model for storing Nursery related details
    """
    __tablename__ = 'preregistrations'

    uuid: str = Column(String, primary_key=True, unique=True, index=True)
    code: str = Column(String, nullable=False)

    child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=True)
    child: Mapped[any] = relationship("Child", foreign_keys=child_uuid, uselist=False, back_populates="preregistrations")

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    contract_uuid: str = Column(String, ForeignKey('contracts.uuid'), nullable=True)
    contract: Mapped[any] = relationship("Contract", foreign_keys=contract_uuid, uselist=False)

    note: str = Column(String, default="")
    status: str = Column(types.Enum(PreRegistrationStatusType), nullable=False, default=PreRegistrationStatusType.PENDING)

    # tags = relationship("Tags",back_populates="preregistrations", uselist=True)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(PreRegistration, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(PreRegistration, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()

