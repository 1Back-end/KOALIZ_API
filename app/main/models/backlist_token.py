from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, String, event

from app.main.models.db.base_class import Base


@dataclass
class BlacklistToken(Base):
    __tablename__ = 'blacklist_tokens'

    uuid = Column(String, primary_key=True, unique=True)
    token = Column(String(500), unique=False, nullable=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<BlacklistToken: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(db, auth_token):
        # check whether auth token has been blacklisted
        res = db.query(BlacklistToken).filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False


@event.listens_for(BlacklistToken, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(BlacklistToken, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()
