from datetime import datetime, timedelta
import math
from typing import Union, Optional, List
from pydantic import EmailStr
from app.main.core.i18n import __
from app.main.core.mail import send_account_creation_email, send_reset_password_email
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload
from app.main import schemas, models
from dateutil.relativedelta import relativedelta

import uuid
from app.main.core.security import get_password_hash, verify_password,generate_code


class CRUDMembership(CRUDBase[models.Membership, schemas.MembershipCreate,schemas.MembershipUpdate]):
    
    
    @classmethod
    def get_period_status(cls, db: Session, period_from: datetime, period_to: datetime) -> dict:
        """
        Détermine si aujourd'hui est avant, pendant, ou après une période donnée.
        
        :param db: Session de la base de données (non utilisé ici mais peut être nécessaire pour des extensions futures).
        :param period_from: Date de début de la période.
        :param period_to: Date de fin de la période.
        :return: Un dictionnaire indiquant si aujourd'hui est avant, pendant, ou après la période.
        """
        today = datetime.now().date()
        is_within_period = period_from.date() <= today <= period_to.date()
        is_before_period = today < period_from.date()
        # is_after_period = today > period_to.date()

        status = "ACTIVED" if is_within_period else "PENDING" if is_before_period else "UNACTIVED" 

        return status
    
    @classmethod
    def convert_period_to_hours(cls,period_from: datetime, period_to: datetime) -> int:
        """
        Convertit une période donnée de period_from à period_to en heures.

        :param period_from: La date et l'heure de début de la période.
        :param period_to: La date et l'heure de fin de la période.
        :return: La durée de la période en heures.
        """
        # Calculer la différence entre period_to et period_from
        period_difference = period_to - period_from
        
        # Convertir la différence en heures
        hours = period_difference.total_seconds() / 3600
        
        return int(hours)
    
    @classmethod
    def get_period_duration(cls, period_unit: str, period_from: datetime, period_to: datetime) -> float:
        if period_unit.lower() == "day":
            return (period_to - period_from).days
        elif period_unit.lower() == "month":
            delta = relativedelta(period_to, period_from)
            return delta.years * 12 + delta.months + delta.days / 30  # Approximation pour les jours
        elif period_unit.lower() == "year":
            delta = relativedelta(period_to, period_from)
            return delta.years + delta.months / 12 + delta.days / 365  # Approximation pour les mois et les jours
    
    # @classmethod
    # def is_today_within_period(period_from: datetime, period_to: datetime) -> bool:
    #     today = datetime.now().date()
    #     return period_from.date() <= today <= period_to.date()
    
    # @classmethod
    # def is_today_before_period_from(cls, db: Session, period_from: datetime) -> bool:
    #     today = datetime.now().date()
    #     return  today < period_from.date()
    
    # @classmethod
    # def is_today_after_period_to(cls, db: Session, period_to: datetime) -> bool:
    #     today = datetime.now().date()
    #     return today > period_to.date()
    
    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Optional[models.Membership]:
        return db.query(models.Membership).filter(models.Membership.uuid == uuid).first()
    
    @classmethod
    def update_status(cls, db:Session, uuid:str, status:str):
        membership = cls.get_by_uuid(db, uuid)
        membership.status = status
        db.commit()
        db.refresh(membership)
    
    # @classmethod
    # def get_membershiptype(cls,db:Session, uuid:str):
    #     return db.query(models.MembershipType).filter(models.MembershipType.uuid == uuid).first()
        
    @classmethod
    def create(cls, db: Session, obj_in: schemas.MembershipCreate) -> models.Membership:
        status = cls.get_period_status(db, obj_in.period_from,obj_in.period_to)
        membership = models.Membership(
            uuid= str(uuid.uuid4()),
            title_fr = obj_in.title_fr,
            title_en = obj_in.title_en,
            owner_uuid= obj_in.owner_uuid,
            description = obj_in.description if obj_in.description else None,
            period_unit = obj_in.period_unit,
            period_from = obj_in.period_from,
            duration = cls.get_period_duration(obj_in.period_unit, obj_in.period_from, obj_in.period_to),
            period_to = obj_in.period_to if obj_in.period_to else None,
            status = cls.update_status(db, uuid, status)
        )
        db.add(membership)
        db.commit()
        db.refresh(membership)

    @classmethod
    def update(cls, db: Session, obj_in: schemas.MembershipUpdate) -> models.Membership:
        status = cls.get_period_status(db, obj_in.period_from,obj_in.period_to)
        membership = cls.get_by_uuid(db, obj_in.uuid)
        membership.title_fr = obj_in.title_fr if obj_in.title_fr else membership.title_fr
        
        membership.title_en = obj_in.title_en if obj_in.title_en else membership.title_en
        membership.description = obj_in.description if obj_in.description else membership.description
        membership.owner_uuid = obj_in.owner_uuid if obj_in.owner_uuid else membership.owner_uuid

        membership.period_from = obj_in.period_from if obj_in.period_from else membership.period_from
        membership.period_to = obj_in.period_to if obj_in.period_to else membership.period_to
        membership.period_unit = obj_in.period_unit if obj_in.period_unit else membership.period_unit
        
        if obj_in.period_unit and obj_in.period_from and obj_in.period_to:
            membership.duration = cls.get_period_duration(obj_in.period_unit, obj_in.period_from, obj_in.period_to)
        
        membership.status = cls.update_status(db, obj_in.uuid, status)
        db.commit()
        db.refresh(membership)
    
        return membership
    
    @classmethod
    def get_multi(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 30,
        order:Optional[str] = None,
        status:Optional[str] = None,
        period_unit:Optional[str] = None,
        period_from:Optional[str] = None,
        period_to: Optional[str] = None,
        duration:Optional[str] = None,
        owner_uuid:Optional[str] = None
    ):
        record_query = db.query(models.Membership)

        # if order_filed:
        #     record_query = record_query.order_by(getattr(models.Administrator, order_filed))

        # record_query = record_query.filter(models.Administrator.status.not_in(["DELETED","BLOCKED"]))
        if owner_uuid:
            record_query = record_query.filter(models.Membership.owner_uuid == owner_uuid)
            
        if duration:
            record_query = record_query.filter(models.Membership.duration == duration)

        if status:
            record_query = record_query.filter(models.Membership.status == status)
        
        if period_unit:
            record_query = record_query.filter(models.Membership.period_unit == period_unit)
            
        if period_to and period_from:
            record_query = record_query.filter(
                models.Membership.period_from >= period_from<= period_to,
                models.Membership.period_to >= period_from<= period_to)
        
        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.Administrator.date_added.asc())
        
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.Administrator.date_added.desc())

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.MembershipResponseList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )

membership = CRUDMembership(models.Membership)
