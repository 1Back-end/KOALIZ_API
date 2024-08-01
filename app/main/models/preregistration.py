from enum import Enum

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, event, types, Date, ARRAY, Float, Boolean
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, date

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship, Mapped
from app.main.models.db.session import SessionLocal
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

    pre_contract_uuid: str = Column(String, ForeignKey('pre_contracts.uuid'), nullable=True)
    pre_contract: Mapped[any] = relationship("PreContract", foreign_keys=pre_contract_uuid, back_populates="child", uselist=False)

    parents: Mapped[list[any]] = relationship("ParentGuest", back_populates="child", uselist=True)

    preregistrations: Mapped[list[any]] = relationship("PreRegistration", back_populates="child", uselist=True)

    added_by_uuid: str = Column(String, ForeignKey('owners.uuid'), nullable=True)
    added_by = relationship("Owner", foreign_keys=[added_by_uuid], uselist=False)
    is_accepted: bool = Column(Boolean, default=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    @hybrid_property
    def paying_parent(self):
        for parent in self.parents:
            if parent.is_paying_parent:
                return parent


@event.listens_for(Child, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(Child, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


class PreContract(Base):
    """
         database model for storing Nursery Opening Hour related details
    """
    __tablename__ = "pre_contracts"

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    begin_date: date = Column(Date, nullable=False)
    end_date: date = Column(Date, nullable=False)
    # typical_weeks: list = relationship("TypicalWeek", backref="pre_contract")
    # typical_weeks: Mapped[list[any]] = relationship("TypicalWeek", back_populates="pre_contract", uselist=True)
    # typical_weeks: list[any] = Column(MutableList.as_mutable(ARRAY(JSONB)), nullable=False)
    typical_weeks: list[any] = Column(MutableList.as_mutable(JSONB), nullable=False)
    child: Mapped[any] = relationship("Child", back_populates="pre_contract", uselist=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(PreContract, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(PreContract, 'before_update')
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

    is_paying_parent: bool = Column(Boolean, default=False)

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


class TrackingCase(Base):

    """ database model for storing tracking cases related details """

    __tablename__ = 'tracking_cases'

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    preregistration_uuid = Column(String, ForeignKey('preregistrations.uuid'), nullable=False)
    preregistration: Mapped[any] = relationship("PreRegistration", back_populates="tracking_cases")

    interaction_type = Column(String, nullable=False)  # Type d'interaction: note, document, meeting, activity-reminder, call
    details = Column(JSONB, nullable=True)  # Détails spécifiques à l'interaction

    # logs = relationship("Log", order_by="Log.date_added", back_populates="tracking_case")

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<TrackingCase: uuid: {} interaction_type: {}>'.format(self.uuid, self.interaction_type)

@event.listens_for(TrackingCase, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()

@event.listens_for(TrackingCase, 'before_update')
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

    pre_contract_uuid: str = Column(String, ForeignKey('pre_contracts.uuid'), nullable=True)
    pre_contract: Mapped[any] = relationship("PreContract", foreign_keys=pre_contract_uuid, uselist=False)

    tracking_cases = relationship("TrackingCase", order_by="TrackingCase.date_added", back_populates="preregistration")
    # logs = relationship("Log", order_by="Log.date_added", back_populates="preregistration")

    refused_date: datetime = Column(DateTime, nullable=True, default=None)
    accepted_date: datetime = Column(DateTime, nullable=True, default=None)

    note: str = Column(String, default="")
    status: str = Column(types.Enum(PreRegistrationStatusType), nullable=False, default=PreRegistrationStatusType.PENDING)

    @hybrid_property
    def tags(self):
        db = SessionLocal()
        from app.main.models import TagElement,Tags  # Importation locale pour éviter l'importation circulaire

        try:
            record = db.query(Tags).\
                outerjoin(TagElement,Tags.uuid == TagElement.tag_uuid).\
                    filter(TagElement.element_uuid == self.uuid,TagElement.element_type == "PRE_ENROLLMENT").\
                        all()
            return record
        finally:
            db.close()
    
    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<PreRegistration: uuid: {} code: {}>'.format(self.uuid, self.code)


@event.listens_for(PreRegistration, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(PreRegistration, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


class ActivityReminderType(Base):
    """
    database model for storing Activity Reminder related details
    """
    __tablename__ = 'activity_reminder_types'

    uuid: str = Column(String, primary_key=True, unique=True, index=True)
    title_fr: str = Column(String, nullable=False)
    title_en: str = Column(String, nullable=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(ActivityReminderType, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(ActivityReminderType, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()

class MeetingType(Base):
    """
    database model for storing meeting types related details
    """
    __tablename__ = 'meeting_types'

    uuid: str = Column(String, primary_key=True, unique=True, index=True)
    title_fr: str = Column(String, nullable=False)
    title_en: str = Column(String, nullable=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(MeetingType, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(MeetingType, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()