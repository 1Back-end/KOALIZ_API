from enum import Enum

from datetime import datetime, date
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, event, types,UniqueConstraint, \
    Float
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, Mapped
from .db.base_class import Base


class InvoiceStatusType(str, Enum):
    INCOMPLETE = "INCOMPLETE"
    PAID = "PAID"
    PENDING = "PENDING"
    PROFORMA = "PROFORMA"
    UNPAID = "UNPAID"


class InvoiceItemType(str, Enum):
    REGISTRATION = "REGISTRATION"
    DEPOSIT = "DEPOSIT"
    ADAPTATION = "ADAPTATION"
    INVOICE = "INVOICE"
    CUSTOM = "CUSTOM"
    OVERTIME = "OVERTIME"


class Invoice(Base):
    """
     database model for storing Nursery related details
    """
    __tablename__ = 'invoices'

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    id: int = Column(Integer, default=0)
    reference: str = Column(String, nullable=False, default="")

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=True)
    child: Mapped[any] = relationship("Child", foreign_keys=child_uuid, uselist=False)

    quote_uuid = Column(String, ForeignKey('quotes.uuid'), nullable=True)
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

    payments: Mapped[list[any]] = relationship("Payment", back_populates="invoice", uselist=True, cascade="all, delete-orphan")

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    @hybrid_property
    def total_hours(self):
        # Check cases in which item.total_hours is not a float
        return sum([item.total_hours for item in self.items if item.total_hours is not None])



    @hybrid_property
    def total_overtime_hours(self):
        return sum([item.total_overtime_hours for item in self.items if item.total_overtime_hours is not None])


@event.listens_for(Invoice, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


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
    total_overtime_hours: float = Column(Float)
    unit_price: float = Column(Float)

    type: str = Column(types.Enum(InvoiceItemType))

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


class ClientAccountContract(Base):
    __tablename__ = 'client_account_contracts'

    uuid: str = Column(String, primary_key=True, unique=True, index=True)
    client_account_uuid: str = Column(String, ForeignKey('client_accounts.uuid'), nullable=False)
    client_account = relationship("ClientAccount", foreign_keys=client_account_uuid, uselist=False, overlaps="client_accounts")
    # client_account = relationship("ClientAccount", foreign_keys=client_account_uuid, uselist=False, overlaps="teams")

    contract_uuid: str = Column(String, ForeignKey('contracts.uuid'), nullable=False)
    contract = relationship("Contract", foreign_keys=contract_uuid, uselist=False, overlaps="client_accounts")

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(ClientAccountContract, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()

@event.listens_for(ClientAccountContract, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


@event.listens_for(InvoiceItem, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


class ClientAccountChild(Base):
    __tablename__ = 'client_account_children'

    uuid: str = Column(String, primary_key=True, unique=True, index=True)
    client_account_uuid: str = Column(String, ForeignKey('client_accounts.uuid'), nullable=False)
    client_account = relationship("ClientAccount", foreign_keys=client_account_uuid, uselist=False, overlaps="client_accounts")
    # client_account = relationship("ClientAccount", foreign_keys=client_account_uuid, uselist=False, overlaps="teams")

    child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=False)
    child = relationship("Child", foreign_keys=child_uuid, uselist=False, overlaps="client_accounts")

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(ClientAccountChild, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()

@event.listens_for(ClientAccountChild, 'before_update')
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
    account_number: str = Column(String, default="")
    entity_name: str = Column(String, default="")
    iban: str = Column(String, default="")
    address: str = Column(String, nullable=False)
    zip_code: str = Column(String, nullable=False)
    city: str = Column(String, nullable=False)
    country: str = Column(String, nullable=False)
    phone_number: str = Column(String, nullable=False)
    email: str = Column(String, nullable=False)

    invoices: Mapped[list[any]] = relationship("Invoice", uselist=True, back_populates="client_account")
    contracts = relationship("Contract", secondary="client_account_contracts", back_populates="client_accounts", uselist=True, overlaps="contract,client_account")
    children = relationship("Child", secondary="client_account_children", back_populates="client_accounts", uselist=True, overlaps="child,client_account")
    # children = relationship("Employee", secondary="client_account_children", back_populates="client_accounts", overlaps="employee,client_account")

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


class PaymentType(Enum):
    PARTIAL = "PARTIAL"
    TOTAL = "TOTAL"


class PaymentMethod(Enum):
    CASH = "CASH"
    CREDIT_CARD = "CREDIT_CARD"
    SEPA = "SEPA"
    BANK_TRANSFER = "BANK_TRANSFER"


class Payment(Base):
    __tablename__ = 'payments'

    uuid: str = Column(String, primary_key=True, unique=True, index=True)
    type = Column(types.Enum(PaymentType), nullable=False)
    method = Column(types.Enum(PaymentMethod), nullable=False)
    amount = Column(Float, default=0)

    invoice_uuid: str = Column(String, ForeignKey('invoices.uuid'), nullable=False)
    invoice = relationship("Invoice", uselist=False, back_populates="payments")

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())


@event.listens_for(Payment, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(Payment, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()
