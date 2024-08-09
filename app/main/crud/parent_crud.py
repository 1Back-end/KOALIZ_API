from datetime import date, datetime, timedelta
import math
from typing import Union, Optional, List
from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy import or_
from app.main.core.i18n import __
from app.main.core.mail import send_account_creation_email,send_account_confirmation_email
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload
from app.main import schemas, models, crud
import uuid
from app.main.core.security import generate_code, get_password_hash, verify_password, generate_password


class CRUDParent(CRUDBase[models.Parent, schemas.ParentCreate,schemas.ParentUpdate]):

    @classmethod
    def get_children_transmissions(
        self,
        *,
        db : Session,
        date : date = None,
        current_parent : models.Parent = None
    ):
        # Get parent children
        parent_children: models.ParentChild = db.query(models.ParentChild).\
            filter(models.ParentChild.uuid==current_parent.uuid).\
            all()

        children = db.query(models.Child).\
            filter(models.Child.uuid.in_([parent_child.child_uuid for parent_child in parent_children])).\
            all()

        meals = db.query(models.Meal).\
            filter(models.Meal.child_uuid.in_([child.uuid for child in children]), models.Meal.date_added == date).\
            order_by(models.Meal.date_added.desc()).\
            all()
        activities = db.query(models.ChildActivity).\
            filter(models.ChildActivity.child_uuid.in_([child.uuid for child in children]), models.ChildActivity.date_added == date).\
            order_by(models.ChildActivity.date_added.desc()).\
            all()
        naps = db.query(models.Nap).\
            filter(models.Nap.child_uuid.in_([child.uuid for child in children]), models.Nap.date_added == date).\
            order_by(models.Nap.date_added.desc()).\
            all()
        health_records = db.query(models.HealthRecord).\
            filter(models.HealthRecord.child_uuid.in_([child.uuid for child in children]), models.HealthRecord.date_added == date).\
            order_by(models.HealthRecord.date_added.desc()).\
            all()
        hygiene_changes = db.query(models.HygieneChange).\
            filter(models.HygieneChange.child_uuid.in_([child.uuid for child in children]), models.HygieneChange.date_added == date).\
            order_by(models.HygieneChange.date_added.desc()).\
            all()
        observations = db.query(models.Observation).\
            filter(models.Observation.child_uuid.in_([child.uuid for child in children]), models.Observation.date_added == date).\
            order_by(models.Observation.date_added.desc()).\
            all()
        media_uuids = [i.media_uuid for i in db.query(models.children_media).filter(models.children_media.c.child_uuid.in_([child.uuid for child in children])).all()]
        media = db.query(models.Media).\
            filter(models.Media.uuid.in_(media_uuids), models.Media.date_added == date).\
            order_by(models.Media.date_added.desc()).\
            all()

        return {
            "meals": meals,
            "activities": activities,
            "naps": naps,
            "health_records": health_records,
            "hygiene_changes": hygiene_changes,
            "observations": observations,
            "media": media
        }

    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Union[models.Parent, None]:
        return db.query(models.Parent).filter(models.Parent.uuid == uuid).first()

    @classmethod
    def create(cls, db: Session, obj_in: schemas.ParentCreate, code:str=None) -> models.Parent:

        role = crud.role.get_by_code(db=db, code="parent")
        if not role:
            raise HTTPException(status_code=404, detail=__("role-not-found"))

        parent = models.Parent(
            uuid= str(uuid.uuid4()),
            firstname = obj_in.firstname,
            lastname = obj_in.lastname,
            email = obj_in.email,
            password_hash = get_password_hash(obj_in.password),
            role_uuid = role.uuid,
            status = models.UserStatusType.UNACTIVED if code else models.UserStatusType.ACTIVED
        )
        db.add(parent)
        db.flush()

        if code:
            db_code = models.ParentActionValidation(
                uuid=str(uuid.uuid4()),
                code=code,
                user_uuid=parent.uuid,
                value=code,
                expired_date=datetime.now() + timedelta(minutes=30)
            )

            db.add(db_code)
            db.commit()
            send_account_confirmation_email(email_to=obj_in.email, name=(obj_in.firstname+obj_in.lastname),token=code,valid_minutes=30)

        db.commit()
        db.refresh(parent)

        return parent

    @classmethod
    def update(cls, db: Session,obj_in: schemas.ParentUpdate) -> models.Parent:
        parent = cls.get_by_uuid(db, obj_in.uuid)
        parent.firstname = obj_in.firstname if obj_in.firstname else parent.firstname
        parent.lastname = obj_in.lastname if obj_in.lastname else parent.lastname
        parent.avatar_uuid = obj_in.avatar_uuid if obj_in.avatar_uuid else parent.avatar_uuid
        parent.email = obj_in.email if obj_in.email else parent.email
        db.commit()
        db.refresh(parent)
        return parent
    
    @classmethod
    def delete(cls,db:Session, uuids:list[str]) -> models.Parent:
        db.query(models.Parent).filter(models.Parent.uuid.in_(uuids)).delete()
        # db.delete(parents)
        db.commit()

    @classmethod
    def soft_delete(cls,db:Session, uuid) -> models.Parent:
        parent = cls.get_by_uuid(db, uuid)
        parent.status = models.UserStatusType.DELETED
        db.commit()

    @classmethod
    def get_by_email(cls,db:Session,email:EmailStr) -> models.Parent:
        return db.query(models.Parent).filter(models.Parent.email == email).first()

    @classmethod
    def get_multi(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 30,
        order:Optional[str] = None,
        status:Optional[str] = None,
        user_uuid:Optional[str] = None,
        order_filed:Optional[str] = None,  
        keyword:Optional[str]= None
    ):
        record_query = db.query(models.Parent).options(joinedload(models.Parent.role))

        # if order_filed:
        #     record_query = record_query.order_by(getattr(models.Parent, order_filed))

        record_query = record_query.filter(models.Parent.status.not_in(["DELETED","BLOCKED"]))

        print("record_query.first()", record_query.all())
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Parent.firstname.ilike('%' + str(keyword) + '%'),
                    models.Parent.email.ilike('%' + str(keyword) + '%'),
                    models.Parent.lastname.ilike('%' + str(keyword) + '%'),
                    models.Role.title_fr.ilike('%' + str(keyword) + '%'),
                    models.Role.title_en.ilike('%' + str(keyword) + '%'),

                )
            )
        if status:
            record_query = record_query.filter(models.Parent.status == status)

        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.Parent.date_added.asc())

        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.Parent.date_added.desc())

        if user_uuid:
            record_query = record_query.filter(models.Parent.uuid == user_uuid)

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        print("total:",total)
        return schemas.ParentResponseList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )

    @classmethod
    def password_confirmation(cls, db: Session, password1: str,password2:str) -> bool:
        return password1 == password2

    @classmethod
    def authenticate(cls, db: Session, email: str, password: str, role_group: str) -> Optional[models.Parent]:
        db_obj: models.Parent = db.query(models.Parent).filter(
            models.Parent.email == email,
            models.Parent.role.has(models.Role.group == role_group)
        ).first()
        if not db_obj:
            return None
        if not verify_password(password, db_obj.password_hash):
            return None
        return db_obj


    def is_active(self, user: models.Parent) -> bool:
        return user.status == models.UserStatusType.ACTIVED

    @classmethod
    def update_status(cls, db:Session, user: models.Parent, status: str):
        user.status = status
        db.commit()

parent = CRUDParent(models.Parent)


