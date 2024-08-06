from enum import Enum
from dataclasses import dataclass
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, event, types
from datetime import datetime, date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from .db.base_class import Base
from app.main.models.db.session import SessionLocal
from app.main.models import PreRegistration,Membership,ParentGuest,Storage,Child

class TagTypeEnum(str, Enum):
    CHILDREN = "CHILDREN"
    CUSTOMER_ACCOUNT = "CUSTOMER_ACCOUNT"
    TEAM = "TEAM"
    PARENTS = "PARENTS"
    DOCUMENTS = "DOCUMENTS"
    PRE_ENROLLMENT = "PRE_ENROLLMENT"
    PICTURE = "PICTURE"
    BILL = "BILL"
    QUOTE = "QUOTE"


@dataclass
class Tags(Base):
    """
     database model for storing Tags related details
    """
    __tablename__ = 'tags'

    uuid: str = Column(String, primary_key=True, unique=True, index=True)
    title_fr: str = Column(String(100), unique=True, index=True)
    title_en: str = Column(String(100), unique=True, index=True)

    color: str = Column(String, nullable=True)
    icon_uuid: str = Column(String, ForeignKey('storages.uuid'), nullable=True)
    icon = relationship("Storage", foreign_keys=[icon_uuid], uselist=False)

    type:str = Column(types.Enum(TagTypeEnum), index=True, nullable=True)

    tag_elements = relationship("TagElement", back_populates="tag")


    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<Tags: uuid: {} title_fr: {} title_en {}>'.format(self.uuid, self.title_fr, self.title_en)


@event.listens_for(Tags, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(Tags, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


class TagElement(Base):
    """
    database model for storing Tags relationships details.
    """
    __tablename__ = 'tag_elements'

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    tag_uuid: str = Column(String, ForeignKey('tags.uuid',ondelete = "CASCADE",onupdate= "CASCADE"), nullable=False)
    tag = relationship("Tags", foreign_keys=[tag_uuid],uselist=False,back_populates="tag_elements")

    element_uuid: str = Column(String, nullable=False)
    element_type: str = Column(String, nullable=False)

    @hybrid_property
    def element(self):
        db = SessionLocal()
        model_mapping = {
            "PRE_ENROLLMENT": PreRegistration,
            # "MEMEBERSHIP": Membership,
            "CHILDREN": Child,
            "PARENTS": ParentGuest,
            "PICTURE":Storage,
            # "Administrator":Administrator,
            # "CUSTOMER_ACCOUNT": Owner,
            # Ajoutez d'autres mappages ici si nécessaire
        }
        
        if self.tag and self.tag.type:
            try:
                # Pour les cas généraux, utilisez le dictionnaire pour accéder dynamiquement au modèle
                model = model_mapping.get(self.tag.type)
                if model:
                    record = db.query(model).filter(model.uuid == self.element_uuid).first()
                    return record
            finally:
                db.close()
            



    # pre_registration_uuid: str = Column(String, ForeignKey('preregistrations.uuid'), nullable=True)
    # pre_registration = relationship("PreRegistration", foreign_keys=[pre_registration_uuid], uselist=False)

    # child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=True)
    # child = relationship("Child", foreign_keys=[child_uuid], uselist=False)

    # nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    # nursery = relationship("Nursery", foreign_keys=[nursery_uuid], uselist=False)

    # membership_uuid: str = Column(String, ForeignKey('memberships.uuid'), nullable=True)
    # membership = relationship("Membership", foreign_keys=[membership_uuid], uselist=False)

    # role_uuid: str = Column(String, ForeignKey('roles.uuid'), nullable=True)
    # role = relationship("Role", foreign_keys=[role_uuid], uselist=False)

    # administrator_uuid: str = Column(String, ForeignKey('administrators.uuid'), nullable=True)
    # administrator = relationship("Administrator", foreign_keys=[administrator_uuid], uselist=False)

    # address_uuid: str = Column(String, ForeignKey('addresses.uuid'), nullable=True)
    # address = relationship("Address", foreign_keys=[address_uuid], uselist=False)

    # owner_uuid: str = Column(String, ForeignKey('owners.uuid'), nullable=True)
    # owner = relationship("Owner", foreign_keys=[owner_uuid], uselist=False)



    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    

@event.listens_for(Tags, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(Tags, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


    
