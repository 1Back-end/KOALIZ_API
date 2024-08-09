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

    date_to: date = Column(Date)
    invoicing_period_start: date = Column(Date)
    invoicing_period_end: date = Column(Date)
    amount: float = Column(Float, default=0)
    amount_paid: float = Column(Float, default=0)
    amount_due: float = Column(Float, default=0)

    items: Mapped[list[any]] = relationship("InvoiceItem", back_populates="invoice", uselist=True, cascade="all, delete-orphan")

    contract_uuid: str = Column(String, ForeignKey('contracts.uuid'), nullable=True)
    contract: Mapped[any] = relationship("Contract", uselist=False)

    client_account_uuid: str = Column(String, ForeignKey('client_accounts.uuid'))
    client_account: Mapped[any] = relationship("ClientAccount", foreign_keys=client_account_uuid, uselist=False, back_populates="invoices")

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


class InvoiceItem(Base):
    """
     database model for storing Timetable related details
    """
    __tablename__ = "invoice_items"

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    title_fr: str = Column(String, nullable=False)
    title_en: str = Column(String, nullable=False)
    amount: float = Column(Float, nullable=0)
    total_hours: float = Column(Float)
    unit_price: float = Column(Float)

    invoice_uuid: str = Column(String, ForeignKey('invoices.uuid', ondelete='CASCADE'), nullable=False)
    invoice: Mapped[any] = relationship("Invoice", foreign_keys=invoice_uuid, uselist=False, back_populates="items")

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(InvoiceItem, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(InvoiceItem, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


class ClientAccount(Base):
    """
     database model for storing Timetable related details
    """
    __tablename__ = "client_accounts"

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    name: str = Column(String, nullable=False)
    account_number: str = Column(String, nullable=False)
    entity_name: str = Column(String, default="")
    iban: str = Column(String, nullable=False, default="")
    address: str = Column(String, nullable=False)
    zip_code: str = Column(String, nullable=False)
    city: str = Column(String, nullable=False)
    country: str = Column(String, nullable=False)
    phone_number: str = Column(String, nullable=False)
    email: str = Column(String, nullable=False)

    invoices: Mapped[list[any]] = relationship("Invoice", uselist=True, back_populates="client_account")

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(ClientAccount, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(ClientAccount, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()
