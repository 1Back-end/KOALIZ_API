from datetime import date, datetime, timedelta
import math
from typing import Union, Optional, List

from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy import Date, cast, or_

from app.main.core.i18n import __, get_language
from app.main.core.mail import admin_send_new_nursery_email, send_new_nursery_email
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload
from app.main import crud, schemas, models
import uuid
from app.main.core.security import get_password_hash, verify_password, generate_code, generate_slug
from app.main.models.preregistration import Child, PreRegistration, PreRegistrationStatusType


class CRUDNursery(CRUDBase[models.Nursery, schemas.NurseryCreateSchema, schemas.NurseryUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Optional[models.Nursery]:
        return db.query(models.Nursery).filter(models.Nursery.uuid == uuid)\
            .filter(models.Nursery.status.notin_([models.NurseryStatusType.DELETED])).first()

    @classmethod
    def create(cls, db: Session, obj_in: schemas.NurseryCreate, current_user_uuid: str = None) -> models.Nursery:

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

        code_from_name = "".join([word[0] for word in obj_in.name.split(" ")])
        code = code_from_name
        while db.query(models.Nursery).filter(models.Nursery.code == code).first():
            if code == code_from_name:
                code = code + "1"
            else:
                if int(code[-1]) <= 9:
                    code = code_from_name + str(int(code[-1]) + 1)
                elif code[-2] == "99":
                    code = code_from_name + str(int(code[-2]) + 1)
                elif code[-3] == "999":
                    code = code_from_name + str(int(code[-4]) + 1)
                else:
                    code = code_from_name + str(int(code[-5:]) + 1)

        nursery = models.Nursery(
            uuid=str(uuid.uuid4()),
            email=obj_in.email,
            name=obj_in.name,
            code=code,
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
        if not current_user_uuid:
            for admin in crud.administrator.get_all_active(db):
                print(f"admin email: {admin.email}")
                data = {
                    "user_name": f"{admin.firstname} {admin.lastname}".strip(),
                    "nursery_name": nursery.name,
                    "creator_name": f"{nursery.owner.firstname} {nursery.owner.lastname}".strip(),
                }
                admin_send_new_nursery_email(email_to=admin.email, data=data, language=get_language())
        else:
            data = {
                "user_name": f"{nursery.owner.firstname} {nursery.owner.lastname}".strip(),
                "nursery_name": nursery.name,
                "creator_name": f"{nursery.added_by.firstname} {nursery.added_by.lastname}".strip(),
            }
            send_new_nursery_email(email_to=owner.email, data=data, language=get_language())

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
    def delete(cls, db: Session, uuids: list[str], owner_uuid: str = None) -> None:
        uuids = set(uuids)
        nurseries = cls.get_by_uuids(db, uuids, owner_uuid)
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
    def get_by_uuids(cls, db: Session, uuids: list[str], owner_uuid: str = None) -> list[Optional[models.Nursery]]:
        res = db.query(models.Nursery).filter(models.Nursery.uuid.in_(uuids))\
            .filter(models.Nursery.status.notin_([models.NurseryStatusType.DELETED]))
        if owner_uuid:
            res = res.filter(models.Nursery.owner_uuid==owner_uuid)
        return res.all()

    @classmethod
    def get_by_slug(cls, db: Session, slug: str, deleted_included=False) -> Optional[models.Nursery]:
        res = db.query(models.Nursery).filter(models.Nursery.slug == slug)
        if not deleted_included:
            res = res.filter(models.Nursery.status.notin_([models.NurseryStatusType.DELETED]))

        return res.first()


    @classmethod
    def get_all_uuids_of_same_owner(cls, db: Session, owner_uuid: str, except_uuids: list[str] = []) -> list[dict]:
        res = db.query(models.Nursery.uuid, models.Nursery.name).filter(models.Nursery.owner_uuid == owner_uuid).filter(models.Nursery.status != models.NurseryStatusType.DELETED)
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

    def get_employee_home_page(self, *, db: Session, nursery_uuid: str):

        nursery = db.query(models.Nursery).filter(models.Nursery.uuid == nursery_uuid).first()
        if not nursery:
            raise HTTPException(status_code=404, detail="Nursery not found")

        opening_hours = db.query(models.NurseryOpeningHour)\
            .filter(models.NurseryOpeningHour.nursery_uuid == nursery_uuid).\
            all()

        close_hours = db.query(models.NurseryCloseHour).filter(models.NurseryCloseHour.nursery_uuid == nursery_uuid).all()

        holidays = db.query(models.NuseryHoliday).\
            filter(models.NuseryHoliday.nursery_uuid == nursery_uuid).\
            filter(models.NuseryHoliday.is_active == True).\
            all()

        return {
            "opening_hours": opening_hours,
            "close_hours": close_hours,
            "holidays": holidays
        }
    
    def get_children_by_nursery(
            self,*,
            db: Session,
            nursery_uuid: str,
            child_uuid: Optional[str] = None,
            filter_date: Optional[date] = None,
            # page:int=1,
            # per_page: int=30,
            order_filed: str = "date_added",
            order: str = "desc"
            # keyword:Optional[str] = None
            ) -> List[Child]:
        
        # Trouver toutes les préinscriptions acceptées pour la crèche spécifiée
        accepted_preregistrations = db.query(PreRegistration).filter(
            PreRegistration.nursery_uuid == nursery_uuid,
            PreRegistration.status == PreRegistrationStatusType.ACCEPTED
        ).all()

        # Récupérer les UUIDs des enfants acceptés
        child_uuids = [preregistration.child_uuid for preregistration in accepted_preregistrations if preregistration.child_uuid]

        if filter_date:
            end_date = datetime.combine(filter_date, datetime.max.time())
            start_date = datetime.combine(filter_date, datetime.min.time())
            print(start_date)  # Affiche la date avec l'heure 00:00:00
            print(end_date)    # Affiche la date avec l'heure 23:59:59.999999
            child_uuids = [
                child_planning.child_uuid
                for child_planning in
                    db.query(models.ChildPlanning).
                    filter(models.ChildPlanning.child_uuid.in_(child_uuids)).
                    filter(models.ChildPlanning.nursery_uuid==nursery_uuid).
                    filter(models.ChildPlanning.current_date == filter_date).\
                    all()
            ]

        # Filtrer les enfants par UUID et is_accepted
        children = db.query(Child).filter(
            Child.uuid.in_(child_uuids),
            Child.is_accepted == True
        )
        if child_uuid:
            children = children.filter(Child.uuid == child_uuid)

        media_uuids = [i.media_uuid for i in db.query(models.children_media).filter(models.children_media.c.child_uuid.in_([child.uuid for child in children])).all()]


        for child in children:

            child.meals = db.query(models.Meal).\
                    filter(models.Meal.child_uuid == child.uuid, 
                        models.Meal.is_deleted !=True,
                        models.Meal.nursery_uuid == nursery_uuid).\
                        order_by(models.Meal.date_added.desc()).\
                            all()
                
            child.activities = db.query(models.ChildActivity).\
                filter(models.ChildActivity.child_uuid == child.uuid,
                        models.ChildActivity.status != models.AbsenceStatusEnum.DELETED,
                        models.ChildActivity.nursery_uuid == nursery_uuid,
                ).\
                    order_by(models.ChildActivity.date_added.desc()).\
                        all()
            
            child.naps = db.query(models.Nap).\
                filter(models.Nap.child_uuid == child.uuid,
                    models.Nap.status !=models.AbsenceStatusEnum.DELETED,
                    models.Nap.nursery_uuid == nursery_uuid,
                ).\
                    order_by(models.Nap.date_added.desc()).\
                        all()
            
            child.health_records = db.query(models.HealthRecord).\
                filter(models.HealthRecord.child_uuid == child.uuid,
                    models.HealthRecord.status !=models.AbsenceStatusEnum.DELETED,
                    models.HealthRecord.nursery_uuid == nursery_uuid
                ).\
                order_by(models.HealthRecord.date_added.desc()).\
                    all()
            
            child.hygiene_changes = db.query(models.HygieneChange).\
                filter(models.HygieneChange.child_uuid == child.uuid,
                        models.HygieneChange.status!= models.AbsenceStatusEnum.DELETED,
                        models.HygieneChange.nursery_uuid == nursery_uuid,
                ).\
                    order_by(models.HygieneChange.date_added.desc()).\
                    all()
            
            child.observations = db.query(models.Observation).\
                filter(models.Observation.child_uuid == child.uuid,
                    models.Observation.status !=models.AbsenceStatusEnum.DELETED,
                    models.Observation.nursery_uuid == nursery_uuid,
                ).\
                    order_by(models.Observation.date_added.desc()).\
                        all()
            
            child.media = db.query(models.Media).\
                filter(models.Media.uuid.in_(media_uuids),
                    models.Media.status!=models.AbsenceStatusEnum.DELETED,
                    models.Media.nursery_uuid == nursery_uuid, 
                ).\
                    order_by(models.Media.date_added.desc()).\
                        all()
            if filter_date:
                print("when-filter-date23:",filter_date)

                # Step 2: Load filtered relations and assign to the child object
                child.meals = db.query(models.Meal).\
                    filter(models.Meal.child_uuid == child.uuid, 
                        models.Meal.date_added.between(start_date,end_date), # Ajout du filtre conditionnel
                        models.Meal.is_deleted !=True,
                        models.Meal.nursery_uuid == nursery_uuid).\
                        order_by(models.Meal.date_added.desc()).\
                            all()
                
                print("exist-meal",child.meals)
                child.activities = db.query(models.ChildActivity).\
                    filter(models.ChildActivity.child_uuid == child.uuid,models.ChildActivity.status != models.AbsenceStatusEnum.DELETED,
                            models.ChildActivity.nursery_uuid == nursery_uuid,
                            models.ChildActivity.date_added.between(start_date,end_date)
                        ).\
                            order_by(models.ChildActivity.date_added.desc()).\
                            all()
                
                child.naps = db.query(models.Nap).\
                    filter(models.Nap.child_uuid == child.uuid,
                        models.Nap.status !=models.AbsenceStatusEnum.DELETED,
                        models.Nap.nursery_uuid == nursery_uuid,
                        models.Nap.date_added.between(start_date,end_date)).\
                        order_by(models.Nap.date_added.desc()).\
                            all()
                
                child.health_records = db.query(models.HealthRecord).\
                    filter(models.HealthRecord.child_uuid == child.uuid,
                        models.HealthRecord.status !=models.AbsenceStatusEnum.DELETED,
                        models.HealthRecord.nursery_uuid == nursery_uuid,
                        models.HealthRecord.date_added.between(start_date,end_date)).\
                            order_by(models.HealthRecord.date_added.desc()).\
                            all()
                
                child.hygiene_changes = db.query(models.HygieneChange).\
                    filter(models.HygieneChange.child_uuid == child.uuid,
                        models.HygieneChange.status!= models.AbsenceStatusEnum.DELETED,
                        models.HygieneChange.nursery_uuid == nursery_uuid,
                        models.HygieneChange.date_added.between(start_date,end_date)).\
                        order_by(models.HygieneChange.date_added.desc()).\
                            all()
                
                child.observations = db.query(models.Observation).\
                    filter(models.Observation.child_uuid == child.uuid,
                        models.Observation.status !=models.AbsenceStatusEnum.DELETED,
                        models.Observation.nursery_uuid == nursery_uuid,
                        models.Observation.date_added.between(start_date,end_date)).\
                        order_by(models.Observation.date_added.desc()).\
                            all()
                
                child.media = db.query(models.Media).\
                    filter(models.Media.uuid.in_(media_uuids),
                        models.Media.status!=models.AbsenceStatusEnum.DELETED,
                        models.Media.nursery_uuid == nursery_uuid,
                        models.Media.date_added.between(start_date,end_date)).\
                        order_by(models.Media.date_added.desc()).\
                    all()
                
                

        # if keyword:
        #     children = children.filter(
        #         or_(
        #             models.Child.firstname.ilike('%' + str(keyword) + '%'),
        #             models.Child.lastname.ilike('%' + str(keyword) + '%'),
        #             models.Child.birthplace.ilike('%' + str(keyword) + '%'),
        #             models.Child.gender.ilike('%' + str(keyword) + '%'),
        #         )
        #     )

        # if child_uuid:
        #     children = children.filter(Child.uuid == child_uuid)

        if order == "asc":
            children = children.order_by(getattr(models.Child, order_filed).asc())
        else:
            children = children.order_by(getattr(models.Child, order_filed).desc())


        # total = children.count()
        # children = children.offset((page - 1) * per_page).limit(per_page)


        return children


    def get_number_children_per_day_in_current_week(self, db: Session, nursery: models.Nursery):
        # Get days(Monday to Friday) date of the current week
        days = []
        today = date.today()
        current_week_day = today.weekday()
        monday = today - timedelta(days=current_week_day)
        for i in range(5):
            days.append(monday + timedelta(days=i))

        # Get the number of children per day in the current week
        children_per_day = []
        for day in days:
            children_per_day.append(
                db.query(models.ChildPlanning).filter(
                    models.ChildPlanning.nursery_uuid == nursery.uuid,
                    models.ChildPlanning.current_date == day
                ).count()
            )

        return children_per_day



nursery = CRUDNursery(models.Nursery)


