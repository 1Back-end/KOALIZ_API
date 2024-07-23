from sqlalchemy import Column, String, DateTime,event, ForeignKey
from datetime import datetime
from .db.base_class import Base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped



class Log(Base):

    """ database model for storing logs related details """

    __tablename__ = 'logs'

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    added_by_uuid: str = Column(String, nullable=False)
    before_details = Column(JSONB, nullable=True)
    after_details = Column(JSONB, nullable=True)
    
    preregistration_uuid = Column(String, ForeignKey('preregistrations.uuid'), nullable=False)
    preregistration: Mapped[any] = relationship("PreRegistration", back_populates="logs")

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<Log: uuid: {}>'.format(self.uuid)


@event.listens_for(Log, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(Log, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()