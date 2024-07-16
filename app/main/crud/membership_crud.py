from datetime import datetime, timedelta
import math
from typing import Union, Optional, List
from pydantic import EmailStr
from app.main.core.i18n import __
from app.main.core.mail import send_account_creation_email, send_reset_password_email
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload
from app.main import schemas, models
import uuid
from app.main.core.security import get_password_hash, verify_password,generate_code


class CRUDMembership(CRUDBase[models.Membership, schemas.MembershipCreate,schemas.MembershipUpdate]):
    
    @classmethod
    def is_today_within_period(period_from: datetime, period_to: datetime) -> bool:
        today = datetime.now().date()
        return period_from.date() <= today <= period_to.date()
    
    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Optional[models.Membership]:
        return db.query(models.Membership).filter(models.Membership.uuid == uuid).first()
    
    @classmethod
    def update_status(cls, db:Session, uuid:str, status:str):
        membership = cls.get_by_uuid(db, uuid)
        membership.status = status
        db.commit()
        db.refresh(membership)
        
    @classmethod
    def create(cls, db: Session, obj_in: schemas.MembershipCreate) -> models.Membership:
        membership = models.Membership(
            uuid= str(uuid.uuid4()),
            title_fr = obj_in.title_fr,
            title_en = obj_in.title_en,
            description = obj_in.description if obj_in.description else None,
            price = obj_in.price,
            period_from = obj_in.period_from,
            period_to = obj_in.period_to,
            status = cls.update_status(db, uuid, "status")
        )
        db.add(membership)
        db.commit()
        db.refresh(membership)
    
        return membership

membership = CRUDMembership(models.Membership)
