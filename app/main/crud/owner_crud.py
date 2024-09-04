from datetime import datetime, timedelta
import math
from typing import Union, Optional, List

from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy import or_

from app.main.core.i18n import __, get_language
from app.main.core.mail import send_account_confirmation_email, send_account_creation_email
from app.main.crud.base import CRUDBase
from app.main.crud.role_crud import role as crud_role
from sqlalchemy.orm import Session,joinedload
from app.main import crud, schemas, models
from app.main.core.config import Config
import uuid
from app.main.core.security import generate_code, get_password_hash, verify_password, generate_password


class CRUDOwner(CRUDBase[models.Owner, schemas.AdministratorCreate, schemas.AdministratorUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Union[models.Owner, None]:
        return db.query(models.Owner).filter(models.Owner.uuid == uuid)\
            .filter(models.Owner.status.notin_([models.UserStatusType.BLOCKED, models.UserStatusType.DELETED])).first()

    @classmethod
    def get_by_email(cls, db: Session, email: EmailStr) -> models.Owner:
        return db.query(models.Owner).filter(models.Owner.email == email)\
            .filter(models.Owner.status.notin_([models.UserStatusType.BLOCKED, models.UserStatusType.DELETED])).first()
    
    @classmethod
    def create(cls, db: Session, obj_in: schemas.AdministratorCreate, added_by_uuid) -> models.Owner:
        password: str = generate_password(8, 8)
        print(f"Owner password: {password}")
        role = crud_role.get_by_code(db=db, code="owner")
        if not role:
            raise HTTPException(status_code=404, detail=__("role-not-found"))

        user = models.Owner(
            uuid= str(uuid.uuid4()),
            email = obj_in.email,
            firstname = obj_in.firstname,
            lastname = obj_in.lastname,
            phone_number = obj_in.phone_number,
            password_hash = get_password_hash(password),
            role_uuid = role.uuid,
            avatar_uuid = obj_in.avatar_uuid if obj_in.avatar_uuid else None,
            added_by_uuid = added_by_uuid,
            status = models.UserStatusType.ACTIVED,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        lang: str = get_language()
        send_account_creation_email(email_to=obj_in.email, prefered_language=lang, name=obj_in.firstname,
                                    password=password, login_link=Config.LOGIN_LINK.format(lang))
        return user
    
    @classmethod
    def update(cls, db: Session, user: models.Owner, obj_in: Union[schemas.OwnerUpdate, dict]) -> models.Administrator:
        if type(obj_in) != dict:
            obj_in = obj_in.model_dump(exclude_unset=True)
        return super().update(models.Owner, db, db_obj=user, obj_in=obj_in)

    @classmethod
    def delete(cls, db: Session, uuids: list[str]) -> None:
        uuids = set(uuids)
        users = cls.get_by_uuids(db, uuids)
        if len(uuids) != len(users):
            raise HTTPException(status_code=404, detail=__("user-not-found"))
        for user in users:
            user.status = models.UserStatusType.DELETED
            db.commit()

    
    @classmethod
    def get_multi(
        cls,
        db: Session,
        page: int = 1,
        per_page: int = 30,
        order: Optional[str] = None,
        order_filed: Optional[str] = None,
        keyword: Optional[str] = None,
    ):
        record_query = db.query(models.Owner).filter(models.Owner.status != models.UserStatusType.DELETED)
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Owner.firstname.ilike('%' + str(keyword) + '%'),
                    models.Owner.lastname.ilike('%' + str(keyword) + '%'),
                    models.Owner.email.ilike('%' + str(keyword) + '%'),
                )
            )

        if order == "asc":
            record_query = record_query.order_by(getattr(models.Owner, order_filed).asc())
        else:
            record_query = record_query.order_by(getattr(models.Owner, order_filed).desc())

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.OwnerList(
            total=total,
            pages=math.ceil(total/per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )


    @classmethod
    def authenticate(cls, db: Session, email: str, password: str, role_group: str) -> Optional[models.Owner]:
        db_obj: models.Owner = db.query(models.Owner).filter(
            models.Owner.email == email,
            models.Owner.role.has(models.Role.group == role_group)
        ).first()
        if not db_obj:
            return None
        if not verify_password(password, db_obj.password_hash):
            return None
        return db_obj


    def is_active(self, user: models.Administrator) -> bool:
        return user.status == models.UserStatusType.ACTIVED


    @classmethod
    def get_by_uuids(cls, db: Session, uuids: list[str]) -> list[Optional[models.Owner]]:
        return db.query(models.Owner).filter(models.Owner.uuid.in_(uuids))\
            .filter(models.Owner.status.notin_([models.UserStatusType.DELETED])).all()
    
    @classmethod
    def give_parent_pickup_child_authorization_for_nursery(cls, db: Session, obj_in: schemas.ChildrenConfirmation, added_by: models.Owner):
        
        parent = crud.parent.get_by_email(db, obj_in.parent_email)

        exist_pickup_parent_child_for_nursery  = db.query(models.PickUpParentChild).\
            filter(models.PickUpParentChild.parent_email == obj_in.parent_email).\
            filter(models.PickUpParentChild.child_uuid == obj_in.child_uuid).\
            filter(models.PickUpParentChild.nursery_uuid == obj_in.nursery_uuid).\
            first()
        
        if not exist_pickup_parent_child_for_nursery:
            exist_pickup_parent_child_for_nursery = models.PickUpParentChild(
                uuid= str(uuid.uuid4()),
                parent_uuid = parent.uuid,
                parent_email = obj_in.parent_email,
                nursery_uuid = obj_in.nursery_uuid,
                child_uuid = obj_in.child_uuid,
                added_by_uuid = added_by.uuid
            )
            db.add(exist_pickup_parent_child_for_nursery)
            db.commit()
            db.refresh(exist_pickup_parent_child_for_nursery)
    
        return exist_pickup_parent_child_for_nursery
    
    @classmethod
    def confirm_apps_authorization(cls, db: Session, obj_in: schemas.ChildrenConfirmation, added_by: models.Owner,preregistration:models.PreRegistration):
        
        is_parent_guest = False
        parent = db.query(models.Parent).filter(models.Parent.email.ilike(obj_in.parent_email)).first()
        if not parent:
            is_parent_guest = True
            parent = db.query(models.ParentGuest).filter(models.ParentGuest.email.ilike(obj_in.parent_email)).first()

        parent_child  = db.query(models.ParentChild).\
            filter(models.ParentChild.parent_email == obj_in.parent_email).\
            filter(models.ParentChild.child_uuid == obj_in.child_uuid).\
            filter(models.ParentChild.nursery_uuid == obj_in.nursery_uuid).\
            first()
        
        if obj_in.status in ['REFUSED']:
            db.delete(parent_child)
            db.commit()
            parent_child = None
        
        else:
        
            if not parent_child:
                parent_child = models.ParentChild(
                    uuid= str(uuid.uuid4()),
                    parent_uuid = parent.uuid,
                    parent_email = obj_in.parent_email,
                    nursery_uuid = obj_in.nursery_uuid,
                    child_uuid = obj_in.child_uuid,
                    added_by_uuid = added_by.uuid
                )
                db.add(parent_child)
                db.flush()
                
            if is_parent_guest == True:
                contract = crud.contract.get_contract_by_uuid(db=db, uuid=preregistration.contract_uuid)
                if contract:
                    parent = db.query(models.ParentGuest).filter(models.ParentGuest.uuid == parent_child.parent_uuid).first()
                    if parent:
                        if contract not in parent.contracts:
                            parent.contracts.append(contract)

                # To check this TODO
                # code = generate_code(length=12)
                # code= str(code[0:6]) 
                
                parent.is_new_user = True
                
                # user_code: models.ParentActionValidation = db.query(models.ParentActionValidation).filter(
                # models.ParentActionValidation.user_uuid == parent.uuid)

                # if user_code.count() > 0:
                #     user_code.delete()

                # # print("user_code1:")
                # db_code = models.ParentActionValidation(
                #     uuid=str(uuid.uuid4()),
                #     code=code,
                #     user_uuid=parent.uuid,
                #     value=code,
                #     expired_date=datetime.now() + timedelta(minutes=30)
                # )

                # db.add(db_code)
                # db.commit()

                role = crud.role.get_by_code(db=db, code="parent")
                if not role:
                    raise HTTPException(status_code=404, detail=__("role-not-found"))
                    
                # Generate password and send to user : username and password on the email
                password = generate_password()
                print("Parent Guest: ", password)
                parent.password_hash = get_password_hash(password)

                parent.role_uuid = role.uuid,
                parent.status = models.UserStatusType.ACTIVED
                db.commit()
                db.refresh(parent)

                # send_account_confirmation_email(email_to=parent.email, name=(parent.firstname+parent.lastname), token=code, valid_minutes=30)

            db.commit()
            db.refresh(parent_child)

        return parent_child
    
owner = CRUDOwner(models.Owner)


