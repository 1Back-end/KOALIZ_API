from enum import Enum

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Table, event, types, Date, ARRAY, Float, Boolean
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, date
from sqlalchemy.orm import joinedload

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped
from app.main.models.db.session import SessionLocal
from app.main.models.quote import FamilyType
from .db.base_class import Base
from .children import children_media


class PreRegistrationStatusType(str, Enum):
    ACCEPTED = "ACCEPTED"
    PENDING = "PENDING"
    REFUSED = "REFUSED"
    DELETED = "DELETED"


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


class ContractType(str, Enum):
    REGULAR = "REGULAR"
    OCCASIONAL = "OCCASIONAL"


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

    contract_uuid: str = Column(String, ForeignKey('contracts.uuid'), nullable=True)
    contract: Mapped[any] = relationship("Contract", foreign_keys=contract_uuid, back_populates="child", uselist=False)

    parents: Mapped[list[any]] = relationship("ParentGuest", back_populates="child", uselist=True)

    pickup_parents: Mapped[list[any]] = relationship("PickUpParentChild", back_populates="child", uselist=True)
    app_parents: Mapped[list[any]] = relationship("ParentChild", back_populates="child", uselist=True)

    preregistrations: Mapped[list[any]] = relationship("PreRegistration", back_populates="child", uselist=True)

    meals: Mapped[list[any]] = relationship("Meal", back_populates="child", uselist=True) # Repas
    activities: Mapped[list[any]] = relationship("ChildActivity", back_populates="child", uselist=True) # Activités
    naps: Mapped[list[any]] = relationship("Nap", back_populates="child", uselist=True) # Siestes
    health_records: Mapped[list[any]] = relationship("HealthRecord", back_populates="child", uselist=True) # Santés
    hygiene_changes: Mapped[list[any]] = relationship("HygieneChange", back_populates="child", uselist=True) # Hygienes
    media: Mapped[list[any]] = relationship("Media", secondary=children_media, back_populates="children", uselist=True) # Media
    observations: Mapped[list[any]] = relationship("Observation", back_populates="child", uselist=True) # Observations
    attendances: Mapped[list[any]] = relationship("Attendance", back_populates="child", uselist=True) # Attendances (Presences)

    added_by_uuid: str = Column(String, ForeignKey('owners.uuid'), nullable=True)
    added_by = relationship("Owner", foreign_keys=added_by_uuid, uselist=False)
    is_accepted: bool = Column(Boolean, default=False)
    family_type: str = Column(types.Enum(FamilyType), default=FamilyType.COUPLE, nullable=True)

    client_accounts: Mapped[list[any]] = relationship("ClientAccount", secondary="client_account_children", back_populates="children", uselist=True)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    @hybrid_property
    def paying_parent(self):
        for parent in self.parents:
            if parent.is_paying_parent:
                return parent
        if len(self.parents) > 0:
            return self.parents[0]
    
    @hybrid_property
    def age(self):
        current_year = datetime.now().date().year
        birthday_year = self.birthdate.year

        return current_year - birthday_year
    
    @hybrid_property
    def nb_parent(self):
        """ Return the number of parents for this child """
        return len(self.parents)
    
    @hybrid_property
    def accepted_date(self):
        db = SessionLocal()

        """Return the date when this child was accepted"""
        try:
            pre_registration = db.query(PreRegistration).\
                filter(PreRegistration.child_uuid == self.uuid).\
                filter(PreRegistration.status == PreRegistrationStatusType.ACCEPTED).\
                first()
            return pre_registration.accepted_date.date()
        finally:
            db.close()

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
    typical_weeks: list[any] = Column(JSONB, nullable=False)
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


class ParentChild(Base):

    """ database model for storing parent children cases related details """

    __tablename__ = 'parent_children'

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    parent_uuid = Column(String, ForeignKey('parents.uuid'), nullable=True)
    parent: Mapped[any] = relationship("Parent", foreign_keys=parent_uuid, uselist=False)

    parent_email = Column(String, nullable=False)

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=True)
    child: Mapped[any] = relationship("Child", foreign_keys=child_uuid, uselist=False,back_populates="app_parents")

    added_by_uuid: str = Column(String, ForeignKey('owners.uuid'), nullable=True)
    added_by = relationship("Owner", foreign_keys=[added_by_uuid], uselist=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(ParentChild, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()

@event.listens_for(ParentChild, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()

# Table d'association many-to-many entre Parent et Contract
parent_contract = Table('parent_contract', Base.metadata,
    Column('contract_uuid', String, ForeignKey('contracts.uuid'), primary_key=True),
    Column('parent_uuid', String, ForeignKey('parents.uuid'), primary_key=True)
)

class PickUpParentChild(Base):
    """
    database model for storing parint whose can pick up children in a nursery
    """

    __tablename__ = "pickup_parent_children"
    
    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    parent_uuid = Column(String, ForeignKey('parents.uuid'), nullable=True)
    parent: Mapped[any] = relationship("Parent", foreign_keys=parent_uuid, uselist=False)

    parent_email = Column(String, nullable=False)

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=True)
    child: Mapped[any] = relationship("Child", foreign_keys=child_uuid, uselist=False,back_populates="pickup_parents")

    added_by_uuid: str = Column(String, ForeignKey('owners.uuid'), nullable=True)
    added_by = relationship("Owner", foreign_keys=[added_by_uuid], uselist=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

@event.listens_for(PickUpParentChild, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()

@event.listens_for(PickUpParentChild, 'before_update')
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

    # contract_uuid: str = Column(String, ForeignKey('contracts.uuid'), nullable=True)
    # contract: Mapped[any] = relationship("Contract", foreign_keys=contract_uuid, uselist=False) #back_populates="parent_guest"

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

    contract_uuid: str = Column(String, ForeignKey('contracts.uuid'), nullable=True)
    contract: Mapped[any] = relationship("Contract", foreign_keys=contract_uuid, uselist=False)

    tracking_cases = relationship("TrackingCase", order_by="TrackingCase.date_added", back_populates="preregistration")
    # logs = relationship("Log", order_by="Log.date_added", back_populates="preregistration")

    refused_date: datetime = Column(DateTime, nullable=True, default=None)
    accepted_date: datetime = Column(DateTime, nullable=True, default=None)

    note: str = Column(String, default="")
    status: str = Column(types.Enum(PreRegistrationStatusType), nullable=False, default=PreRegistrationStatusType.PENDING)
    quote: Mapped[any] = relationship("Quote", back_populates="preregistration", uselist=False)

    @hybrid_property
    def tags(self):
        db = SessionLocal()
        from app.main.models import TagElement,Tags  # Importation locale pour éviter l'importation circulaire

        try:
            record = db.query(Tags).\
                outerjoin(TagElement,Tags.uuid == TagElement.tag_uuid).\
                    filter(TagElement.element_uuid == self.uuid,TagElement.element_type == "PRE_ENROLLMENT").\
                    options(joinedload(Tags.icon)).\
                        all()
            return record
        except Exception as e:
            print(f"Erreur lors de la récupération des tags : {e}")
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


class Contract(Base):
    """
         database model for storing Contract related details
    """
    __tablename__ = "contracts"

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    begin_date: date = Column(Date, nullable=False)
    end_date: date = Column(Date, nullable=False)
    typical_weeks: list[any] = Column(JSONB, nullable=False)
    child: Mapped[any] = relationship("Child", back_populates="contract", uselist=False)
    
    type: str = Column(String, nullable=False)
    status: str = Column(String, nullable=True, default="DRAFT") # DRAFT, ACCEPTED, REFUSED, CANCELLED, TERMINATED, BLOCKED, RUPTURED, DELETED
    
    has_company_contract: bool = Column(Boolean, default=True)
    annual_income: float = Column(Float, default=0)
    caution: float = Column(Float, default=0)

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    parents = relationship("Parent", secondary=parent_contract, back_populates="contracts")

    client_accounts: Mapped[list[any]] = relationship("ClientAccount", secondary="client_account_contracts", back_populates="contracts", uselist=True)

    reference: str = Column(String, default="")
    note: str = Column(String, default="")

    date_of_termination: datetime = Column(DateTime, nullable=True) 
    date_of_acceptation: datetime = Column(DateTime, nullable=True) 
    date_of_rupture: datetime = Column(DateTime, nullable=True) 

    invoice_uuid: str = Column(String, ForeignKey('invoices.uuid'), nullable=True)
    invoice = relationship("Owner", foreign_keys=[invoice_uuid], uselist=False)

    owner_uuid: str = Column(String, ForeignKey('owners.uuid'), nullable=True)
    owner = relationship("Owner", foreign_keys=[owner_uuid], uselist=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    @hybrid_property
    def tags(self):
        db = SessionLocal()
        from app.main.models import TagElement,Tags  # Importation locale pour éviter l'importation circulaire

        try:
            record = db.query(Tags).\
                outerjoin(TagElement,Tags.uuid == TagElement.tag_uuid).\
                    filter(TagElement.element_uuid == self.uuid,TagElement.element_type == "CONTRACT").\
                    options(joinedload(Tags.icon)).\
                        all()
            return record
        except Exception as e:
            print(f"Erreur lors de la récupération des tags : {e}")
        finally:
            db.close()

    @hybrid_property
    def hourly_volume(self):
        total_hours = 0
        
        for week in self.typical_weeks:
            week_hours = 0
            for day in week:
                for period in day:
                    from_time = datetime.strptime(period['from_time'], "%H:%M")
                    to_time = datetime.strptime(period['to_time'], "%H:%M")
                    delta = to_time - from_time
                    hours = delta.total_seconds() / 3600
                    week_hours += hours
            total_hours += week_hours
        
        return total_hours


@event.listens_for(Contract, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(Contract, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


class SEPADirectDebit(Base):
    __tablename__ = 'sepa_direct_debits'

    uuid: str = Column(String, primary_key=True, unique=True, index=True)
    name = Column(String(100), nullable=False)
    iban = Column(String(34), nullable=False, unique=True)
    bic = Column(String(11), nullable=False)
    rum = Column(String(100), nullable=False, unique=True)
    signed_date = Column(Date, nullable=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(SEPADirectDebit, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(SEPADirectDebit, 'before_update')
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