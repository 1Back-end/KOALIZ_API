from sqlalchemy import Column, String, DateTime,event
from datetime import datetime
from app.main.models.db.base_class import Base
from sqlalchemy.dialects.postgresql import JSONB
from app.main.models.db.session import SessionLocal
from sqlalchemy.ext.hybrid import hybrid_property
from app.main import models


class AuditLog(Base):

    """ Database model for storing logs related details """

    __tablename__ = 'audit_logs'

    uuid: str = Column(String, primary_key=True, unique=True, index=True)

    entity_type = Column(String, nullable=False)  # Type d'entité modifiée (ex: 'PreRegistration', 'User', etc.)
    entity_id = Column(String, nullable=False)  # Identifiant de l'entité modifiée
    action = Column(String, nullable=False)  # Action effectuée (ex: 'create', 'update', 'delete')

    performed_by_uuid: str = Column(String, nullable=True)
    before_changes = Column(JSONB, nullable=False)
    after_changes = Column(JSONB, nullable=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    @hybrid_property
    def performed_by(self):
        db = SessionLocal()
        if self.performed_by_uuid:
            current_user = db.query(models.Administrator).filter(models.Administrator.uuid==self.performed_by_uuid).first()
            if not current_user:
                current_user = db.query(models.Owner).filter(models.Owner.uuid==self.performed_by_uuid)
            return current_user
        return None

    def __repr__(self):
        return f'<AuditLog {self.action} on {self.entity_type} by {self.performed_by} at {self.date_added}>'


@event.listens_for(AuditLog, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(AuditLog, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()