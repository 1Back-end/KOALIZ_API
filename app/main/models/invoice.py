from enum import Enum

from datetime import datetime, date
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, event, types,UniqueConstraint, \
    Float
from sqlalchemy.orm import relationship, Mapped
from .db.base_class import Base


class InvoiceStatusType(str, Enum):
    INCOMPLETE = "INCOMPLETE"
    PAID = "PAID"
    PENDING = "PENDING"
    PROFORMA = "PROFORMA"
    UNPAID = "UNPAID"


class Invoice(Base):
    """
     database model for storing Nursery related details
    """
    __tablename__ = 'invoices'

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    reference: str = Column(String, nullable=False, default="")

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=True)
    child: Mapped[any] = relationship("Child", foreign_keys=child_uuid, uselist=False)

    quote_uuid = Column(String, ForeignKey('quotes.uuid'), nullable=False)
    quote: Mapped[any] = relationship("Quote", uselist=False) # , back_populates="invoices"

    parent_guest_uuid: str = Column(String, ForeignKey('parent_guests.uuid'), nullable=True)
    parent_guest: Mapped[any] = relationship("ParentGuest", foreign_keys=parent_guest_uuid, uselist=False)

    status: str = Column(types.Enum(InvoiceStatusType), nullable=False, default=InvoiceStatusType.PROFORMA)

    timetables: Mapped[list[any]] = relationship("InvoiceTimetable", back_populates="invoice", uselist=True, cascade="all, delete-orphan")

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(Invoice, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()
    target.reference = datetime.now().strftime('%Y%m%d%H%M%S')


@event.listens_for(Invoice, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


class InvoiceTimetable(Base):
    """
     database model for storing Timetable related details
    """
    __tablename__ = "invoice_timetables"

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    date_to: date = Column(Date)
    amount: float = Column(Float, default=0)
    amount_paid: float = Column(Float, default=0)
    amount_due: float = Column(Float, default=0)
    status: str = Column(types.Enum(InvoiceStatusType), nullable=False, default=InvoiceStatusType.PROFORMA)

    reference: str = Column(String, nullable=False, default="")
    child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=True)
    child: Mapped[any] = relationship("Child", foreign_keys=child_uuid, uselist=False)

    items: Mapped[list[any]] = relationship("InvoiceTimetableItem", back_populates="timetable", uselist=True, cascade="all, delete-orphan")

    invoice_uuid: str = Column(String, ForeignKey('invoices.uuid', ondelete='CASCADE'), nullable=False)
    invoice: Mapped[any] = relationship("Invoice", foreign_keys=invoice_uuid, uselist=False, back_populates="timetables")

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(InvoiceTimetable, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()
    target.reference = datetime.now().strftime('%Y%m%d%H%M%S')


@event.listens_for(InvoiceTimetable, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


class InvoiceTimetableItem(Base):
    """
     database model for storing Timetable related details
    """
    __tablename__ = "invoice_timetable_items"

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    title_fr: str = Column(String, nullable=False)
    title_en: str = Column(String, nullable=False)
    amount: float = Column(Float, nullable=0)

    timetable_uuid: str = Column(String, ForeignKey('invoice_timetables.uuid', ondelete='CASCADE'), nullable=False)
    timetable: Mapped[any] = relationship("InvoiceTimetable", foreign_keys=timetable_uuid, uselist=False, back_populates="items")

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(InvoiceTimetableItem, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(InvoiceTimetableItem, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()
