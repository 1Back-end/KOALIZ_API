from datetime import datetime, timedelta
import math
from typing import Union, Optional, List

from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy import or_

from app.main.core.i18n import __
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload
from app.main import crud, schemas, models
import uuid
from app.main.core.security import get_password_hash, verify_password, generate_code, generate_slug


class CRUDNursery(CRUDBase[models.Nursery, schemas.NurseryCreateSchema, schemas.NurseryUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Optional[models.Nursery]:
        return db.query(models.Nursery).filter(models.Nursery.uuid == uuid)\
            .filter(models.Nursery.status.notin_([models.NurseryStatusType.DELETED])).first()

    @classmethod
    def create(cls, db: Session, obj_in: schemas.NurseryCreate, current_user_uuid: str) -> models.Administrator:

        if obj_in.logo_uuid:
            logo = crud.storage.get(db=db, uuid=obj_in.logo_uuid)
            if not logo:
                raise HTTPException(status_code=404, detail=__("logo-not-found"))

        if obj_in.signature_uuid:
            signature = crud.storage.get(db=db, uuid=obj_in.signature_uuid)
            if not signature:
                raise HTTPException(status_code=404, detail=__("signature-not-found"))

        if obj_in.stamp_uuid:
            stamp = crud.storage.get(db=db, uuid=obj_in.stamp_uuid)
            if not stamp:
                raise HTTPException(status_code=404, detail=__("stamp-not-found"))

        owner = crud.owner.get_by_uuid(db, obj_in.owner_uuid)
        if not owner:
            raise HTTPException(status_code=404, detail=__("user-not-found"))

        address = crud.address.create(db=db, obj_in=obj_in.address)
        if not address:
            raise HTTPException(status_code=400, detail=__("address-creation-failed"))

        slug = cls.slug_unicity(slug=generate_slug(obj_in.name), db=db)

        nursery = models.Nursery(
            uuid=str(uuid.uuid4()),
            email=obj_in.email,
            name=obj_in.name,
            logo_uuid=obj_in.logo_uuid if obj_in.logo_uuid else None,
            signature_uuid=obj_in.signature_uuid if obj_in.signature_uuid else None,
            stamp_uuid=obj_in.stamp_uuid if obj_in.stamp_uuid else None,
            owner_uuid=obj_in.owner_uuid,
            address_uuid=address.uuid,
            added_by_uuid=current_user_uuid,
            total_places=obj_in.total_places,
            phone_number=obj_in.phone_number,
            website=obj_in.website,
            slug=slug
        )
        db.add(nursery)
        db.commit()
        db.refresh(nursery)
        return nursery
    
    @classmethod
    def update(cls, db: Session, nursery: models.Nursery, obj_in: schemas.NurseryUpdateBase) -> models.Nursery:

        if obj_in.logo_uuid:
            logo = crud.storage.get(db=db, uuid=obj_in.logo_uuid)
            if not logo:
                raise HTTPException(status_code=404, detail=__("logo-not-found"))

        if obj_in.signature_uuid:
            signature = crud.storage.get(db=db, uuid=obj_in.signature_uuid)
            if not signature:
                raise HTTPException(status_code=404, detail=__("signature-not-found"))

        if obj_in.stamp_uuid:
            stamp = crud.storage.get(db=db, uuid=obj_in.stamp_uuid)
            if not stamp:
                raise HTTPException(status_code=404, detail=__("stamp-not-found"))

        address = None
        if not nursery.address and obj_in.address:
            address = crud.address.create(
                db=db,
                obj_in=obj_in.address
            )
            if not address:
                raise HTTPException(status_code=400, detail=__("address-creation-failed"))
        if nursery.address and obj_in.address:
            crud.address.update(
                db=db,
                db_obj=nursery.address,
                obj_in=obj_in.address
            )
        nursery.email = obj_in.email if obj_in.email else nursery.email
        nursery.name = obj_in.name if obj_in.name else nursery.name
        nursery.logo_uuid = obj_in.logo_uuid if obj_in.logo_uuid else None
        nursery.signature_uuid = obj_in.signature_uuid if obj_in.signature_uuid else None
        nursery.stamp_uuid = obj_in.stamp_uuid if obj_in.stamp_uuid else None
        nursery.address_uuid = address.uuid if address else nursery.address_uuid
        nursery.total_places = obj_in.total_places
        nursery.phone_number = obj_in.phone_number

        db.commit()

        return nursery

    @classmethod
    def update_status(cls, db: Session, nursery: models.Nursery, status: models.NurseryStatusType) -> models.Nursery:
        nursery.status = status
        "c0a1fba8-7015-4fff-955b-8ec95df3fdaf"
        db.commit()
        return nursery

    @classmethod
    def delete(cls, db: Session, uuids: list[str]) -> None:
        uuids = set(uuids)
        nurseries = cls.get_by_uuids(db, uuids)
        if len(uuids) != len(nurseries):
            raise HTTPException(status_code=404, detail=__("nursery-not-found"))

        for nursery in nurseries:
            nursery.status = models.NurseryStatusType.DELETED
            db.commit()

    @staticmethod
    def get_many(
            db: Session,
            page: int = 1,
            per_page: int = 30,
            order: Optional[str] = None,
            order_filed: Optional[str] = None,
            keyword: Optional[str] = None,
            status: Optional[str] = None,
            total_places: int = None,
            owner_uuid: str = None,
    ):
        record_query = db.query(models.Nursery)
        if owner_uuid:
            record_query = record_query.filter(models.Nursery.owner_uuid == owner_uuid)
        if status:
            record_query = record_query.filter(models.Nursery.status == status)
        else:
            record_query = record_query.filter(models.Nursery.status != models.NurseryStatusType.DELETED)

        if total_places:
            record_query = record_query.filter(models.Nursery.total_places==total_places)

        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Nursery.name.ilike('%' + str(keyword) + '%'),
                    models.Nursery.email.ilike('%' + str(keyword) + '%'),
                    models.Nursery.phone_number.ilike('%' + str(keyword) + '%'),
                )
            )

        if order == "asc":
            record_query = record_query.order_by(getattr(models.Nursery, order_filed).asc())
        else:
            record_query = record_query.order_by(getattr(models.Nursery, order_filed).desc())

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.NurseryList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )

    @classmethod
    def add_update_opening_hours(cls, db: Session, nursery: models.Nursery, opening_hours: list[schemas.OpeningHoursInput]) -> schemas.OpeningHoursList:
        existing_opening_hours: list[models.NurseryOpeningHour] = db.query(models.NurseryOpeningHour).filter(
            models.NurseryOpeningHour.nursery_uuid == nursery.uuid).all()
        for opening_hour in opening_hours:
            create = True
            for existing_opening_hour in existing_opening_hours:
                if existing_opening_hour.day_of_week == opening_hour.day_of_week:
                    create = False
                    existing_opening_hour.from_time = opening_hour.hours.from_time
                    existing_opening_hour.to_time = opening_hour.hours.to_time
                    break
            if create:
                new_opening_hour = models.NurseryOpeningHour(
                    uuid=str(uuid.uuid4()),
                    day_of_week=opening_hour.day_of_week,
                    from_time=opening_hour.hours.from_time,
                    to_time=opening_hour.hours.to_time,
                    nursery_uuid=nursery.uuid
                )
                db.add(new_opening_hour)
        db.commit()
        db.refresh(nursery)
        return nursery


    @classmethod
    def get_by_uuids(cls, db: Session, uuids: list[str]) -> list[Optional[models.Nursery]]:
        return db.query(models.Nursery).filter(models.Nursery.uuid.in_(uuids))\
            .filter(models.Nursery.status.notin_([models.NurseryStatusType.DELETED])).all()

    @classmethod
    def get_by_slug(cls, db: Session, slug: str, deleted_included=False) -> Optional[models.Nursery]:
        res = db.query(models.Nursery).filter(models.Nursery.slug == slug)
        if not deleted_included:
            res = res.filter(models.Nursery.status.notin_([models.NurseryStatusType.DELETED]))

        return res.first()


    @classmethod
    def get_all_uuids_of_same_owner(cls, db: Session, owner_uuid: str, except_uuids: list[str]) -> list[dict]:
        res = db.query(models.Nursery.uuid, models.Nursery.name).filter(models.Nursery.owner_uuid == owner_uuid)
        if except_uuids:
            res = res.filter(models.Nursery.uuid.notin_(except_uuids))
        return res.all()


    @classmethod
    def slug_unicity(cls, slug: str, db: Session):
        while cls.get_by_slug(db, slug, deleted_included=True):
            slug = f"{slug}-{generate_code(length=4)}"
            return cls.slug_unicity(slug, db)
        return slug

    def is_active(self, user: models.Administrator) -> bool:
        return user.status == models.UserStatusType.ACTIVED


nursery = CRUDNursery(models.Nursery)


