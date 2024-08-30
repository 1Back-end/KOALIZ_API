import math
from calendar import monthrange
from datetime import date, datetime, timedelta
from typing import Union, Optional
from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy import or_
from app.main.core.i18n import __
from app.main.core.mail import send_account_confirmation_email
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload
from app.main import schemas, models, crud
import uuid
from app.main.core.security import  get_password_hash, verify_password
from app.main.models.preregistration import Child


class CRUDParent(CRUDBase[models.Parent, schemas.ParentCreate,schemas.ParentUpdate]):

    @classmethod
    def get_children_transmissions(
        self,
        *,
        nursery_uuid : str,
        db : Session,
        child_uuid: Optional[str] = None,
        filter_date : date = None,
        current_parent : models.Parent = None
    )-> list[Child]:
        # Get parent children
        parent_children: models.ParentChild = db.query(models.ParentChild).\
            filter(models.ParentChild.parent_uuid==current_parent.uuid)
        
        if nursery_uuid:
            parent_children = parent_children.filter(models.ParentChild.nursery_uuid==nursery_uuid)
        
        parent_children = parent_children.all()

        children = db.query(models.Child).\
            filter(models.Child.uuid.in_([parent_child.child_uuid for parent_child in parent_children]))
        
        if child_uuid:
            children = children.filter(models.Child.uuid==child_uuid)

        media_uuids = [i.media_uuid for i in db.query(models.children_media).filter(models.children_media.c.child_uuid.in_([child.uuid for child in children])).all()]

        for child in children:

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
                end_date = datetime.combine(filter_date, datetime.max.time())
                start_date = datetime.combine(filter_date, datetime.min.time())
                print(start_date)  # Affiche la date avec l'heure 00:00:00
                print(end_date)    # Affiche la date avec l'heure 23:59:59.999999

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
                        models.Media.date_added.between(start_date,end_date)).\
                        order_by(models.Media.date_added.desc()).\
                    all()
        
        return children

    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Union[models.Parent, None]:
        return db.query(models.Parent).\
            filter(models.Parent.uuid == uuid,
                   models.Parent.status.not_in([models.UserStatusType.DELETED,models.UserStatusType.BLOCKED])).\
                    first()

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
        parent.fix_phone = obj_in.fix_phone if obj_in.fix_phone else parent.fix_phone
        parent.phone = obj_in.phone if obj_in.phone else parent.phone

        parent.zip_code = obj_in.zip_code if obj_in.zip_code else parent.zip_code
        parent.recipient_number = obj_in.recipient_number if obj_in.recipient_number else parent.recipient_number
        parent.city = obj_in.city if obj_in.city else parent.city

        parent.country = obj_in.country if obj_in.country else parent.country
        parent.profession = obj_in.profession if obj_in.profession else parent.profession
        parent.annual_income = obj_in.annual_income if obj_in.annual_income else parent.annual_income

        parent.company_name = obj_in.company_name if obj_in.company_name else parent.company_name
        parent.has_company_contract = obj_in.has_company_contract if obj_in.has_company_contract else parent.has_company_contract
        parent.dependent_children = obj_in.dependent_children if obj_in.dependent_children else parent.dependent_children
        
        parent.disabled_children = obj_in.disabled_children if obj_in.disabled_children else parent.disabled_children
        parent.is_paying_parent = obj_in.is_paying_parent if obj_in.is_paying_parent else parent.is_paying_parent
        parent.link = obj_in.link if obj_in.link else parent.link
        db.commit()
        db.refresh(parent)
        return parent
    
    @classmethod
    def delete(cls,db:Session, uuids:list[str]) -> models.Parent:
        db.query(models.Parent).filter(models.Parent.uuid.in_(uuids)).delete()
        # db.delete(parents)
        db.commit()

    @classmethod
    def soft_delete(cls,db:Session, uuids):
        for uuid in uuids:
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

        return schemas.ParentResponseList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )
    

    @classmethod
    def get_children(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 30,
        nursery_uuid:Optional[str] = None,
        child_uuid : Optional[str] = None,
        order:Optional[str] = None,
        parent_uuid:Optional[str] = None,
        order_filed:Optional[str] = "date_added",
        keyword:Optional[str]= None
    ):
        # Get parent children
        parent_children: models.ParentChild = db.query(models.ParentChild).\
            filter(models.ParentChild.parent_uuid==parent_uuid)
        
        if nursery_uuid:
            parent_children = parent_children.filter(models.ParentChild.nursery_uuid==nursery_uuid)

        parent_children = parent_children.all()

        record_query = db.query(models.Child).\
            filter(models.Child.uuid.in_([parent_child.child_uuid for parent_child in parent_children]))
        
        if child_uuid:
            record_query = record_query.filter(models.Child.uuid == child_uuid)

        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Child.firstname.ilike('%' + str(keyword) + '%'),
                    models.Child.birthplace.ilike('%' + str(keyword) + '%'),
                    models.Child.lastname.ilike('%' + str(keyword) + '%')
                )
            )

        if order and order.lower() == "asc":
            record_query = record_query.order_by(getattr(models.Child, order_filed).asc())
        else:
            record_query = record_query.order_by(getattr(models.Child, order_filed).desc())

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.ChildDetailsList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page = page,
            data = record_query
        )
    
    @classmethod
    def get_children_media(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 30,
        order:Optional[str] = None,
        parent_uuid:Optional[str] = None,
        order_filed:Optional[str] = "date_added",
        keyword:Optional[str]= None,
        filter_date : date = None,
        media_type:Optional[str]= None,
        child_uuid:Optional[str]= None,
        nursery_uuid : Optional[str] = None
    ):
        # Get parent children
        parent_children: models.ParentChild = db.query(models.ParentChild).\
            filter(models.ParentChild.parent_uuid==parent_uuid).\
            all()
        if nursery_uuid:
            parent_children = parent_children.filter(models.ParentChild.nursery_uuid==nursery_uuid)
        
        if child_uuid:
            parent_children = parent_children.filter(models.ParentChild.child_uuid == child_uuid)

        parent_children  = parent_children.all()

        media = db.query(models.children_media).filter(models.children_media.c.child_uuid.in_([parent_child.child_uuid for parent_child in parent_children])).all()
        
        record_query = db.query(models.Media).\
            filter(
                models.Media.uuid.in_([md.media_uuid for md in media]),
                models.Media.status!= models.AbsenceStatusEnum.DELETED
            )
    
        if filter_date:
            end_date = datetime.combine(filter_date, datetime.max.time())
            start_date = datetime.combine(filter_date, datetime.min.time())
            record_query = record_query.filter(models.Media.date_added.between(start_date, end_date))
        
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Media.observation.ilike('%' + str(keyword) + '%')
                )
            )

        if media_type:
            record_query = record_query.filter(models.Media.media_type == media_type)

        if order and order.lower() == "asc":
            record_query = record_query.order_by(getattr(models.Media, order_filed).asc())
        else:
            record_query = record_query.order_by(getattr(models.Media, order_filed).desc())

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.MediaList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page = page,
            data = record_query
        )

    @classmethod
    def get_invoices(
        cls, 
        db: Session, 
        page: int = 1, 
        per_page: int = 30,
        order: Optional[str] = None, 
        order_filed: Optional[str] = None,
        keyword: Optional[str] = None, 
        status: Optional[str] = None,
        reference: str = None, 
        month: int = None, 
        year: int = None,
        contract_uuid:Optional[str] = None,
        nursery_uuid: Optional[str] = None,
        child_uuid: str = None, 
        parent_uuid: str = None
    ):
        # Get parent children
        parent_children: models.ParentChild = db.query(models.ParentChild).\
            filter(models.ParentChild.parent_uuid==parent_uuid).\
            all()
        
        if nursery_uuid:
            parent_children = parent_children.filter(models.ParentChild.nursery_uuid==nursery_uuid)
        
        if child_uuid:
            parent_children = parent_children.filter(models.ParentChild.child_uuid == child_uuid)
        
        record_query = db.query(models.Invoice).filter(models.Invoice.child_uuid.in_([parent_child.child_uuid for parent_child in parent_children]))

        if status:
            record_query = record_query.filter(models.Invoice.status == status)

        if reference:
            record_query = record_query.filter(models.Invoice.reference == reference)

        if keyword:
            record_query = record_query.filter(models.Invoice.child.has(
                or_(
                    models.Child.firstname.ilike('%' + str(keyword) + '%'),
                    models.Child.lastname.ilike('%' + str(keyword) + '%'),
                ))
            )
        if year and month:
            current_date_start = date(year, month, 1)
            current_date_end = current_date_start.replace(
                day=monthrange(current_date_start.year, current_date_start.month)[1])
            record_query = record_query.filter(models.Invoice.date_to >= current_date_start).filter(
                models.Invoice.date_to <= current_date_end)

        if child_uuid:
            record_query = record_query.filter(models.Invoice.child_uuid == child_uuid)

        if order == "asc":
            record_query = record_query.order_by(getattr(models.Invoice, order_filed).asc())
        else:
            record_query = record_query.order_by(getattr(models.Invoice, order_filed).desc())

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.InvoiceList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
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


