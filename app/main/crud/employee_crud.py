from datetime import datetime, timedelta,timezone
import math
from typing import Optional, Union
from pydantic import EmailStr
from sqlalchemy import or_
from app.main.core.i18n import __
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload 
from app.main import schemas, models
import uuid as py_uuid



class CRUDEmployee(CRUDBase[models.Employee,schemas.EmployeCreate,schemas.EmployeUpdate]):
    
    @classmethod
    def get_by_uuids(cls, db: Session, uuids: list[str]) -> Optional[list[models.Employee]]:
        return db.query(models.Employee).filter(models.Employee.uuid.in_(uuids)).all()
    
    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Union[models.Employee, None]:
        return db.query(models.Employee).filter(models.Employee.uuid == uuid).first()
    
    @classmethod
    def create(cls, db: Session, obj_in: schemas.EmployeCreate) -> models.Employee:
        db_obj = models.Employee(
            uuid= str(py_uuid.uuid4()),
            firstname = obj_in.firstname,
            lastname = obj_in.lastname,
            email = obj_in.email,
            nursery_uuid = obj_in.nursery_uuid,
            avatar_uuid = obj_in.avatar_uuid if obj_in.avatar_uuid else None,
            status = obj_in.status
        )
        db.add(db_obj)
        db.flush()

        if obj_in.team_uuid_tab:
            teams = cls.get_by_uuids(db, obj_in.team_uuid_tab)
            for team in teams:
                if not team in teams:
                    team_members = models.TeamEmployees(
                        uuid= str(py_uuid.uuid4()),
                        employee_uuid = db_obj.uuid,
                        team_uuid = team.uuid
                    )
                    db.add(team_members)
        db.commit()
        db.refresh(db_obj)
    
        return db_obj
    
    @classmethod
    def update(cls, db: Session,obj_in: schemas.EmployeUpdate) -> models.Employee:
        db_obj = cls.get_by_uuid(db, obj_in.uuid)
        db_obj.firstname = obj_in.firstname if obj_in.firstname else db_obj.firstname
        
        db_obj.lastname = obj_in.lastname if obj_in.lastname else db_obj.lastname
        db_obj.email = obj_in.email if obj_in.email else db_obj.email
        
        db_obj.avatar_uuid = obj_in.avatar_uuid if obj_in.avatar_uuid else db_obj.avatar_uuid
        db_obj.team_uuid = obj_in.team_uuid if obj_in.team_uuid else db_obj.team_uuid
        db_obj.nursery_uuid = obj_in.nursery_uuid if obj_in.nursery_uuid else db_obj.nursery_uuid
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @classmethod
    def delete(cls,db:Session, uuid):
        administrator = cls.get_by_uuid(db, uuid)
        db.delete(administrator)
        db.commit()
    
    @classmethod
    def soft_delete(cls,db:Session, uuids:list[str]) -> models.Employee:
        db_obj = cls.get_by_uuid(db, uuids)
        db_obj.status = models.EmployeStatusEnum
        db.commit()
    
    @classmethod
    def get_by_email(cls,db:Session,email:EmailStr) -> models.Employee:
        return db.query(models.Employee).filter(models.Employee.email == email).first()
    
    @classmethod
    def get_multi(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 30,
        order:Optional[str] = None,
        status:Optional[str] = None,
        user_uuid:Optional[str] = None,
        keyword:Optional[str]= None
        # order_filed:Optional[str] = None   
    ):
        record_query = db.query(models.Employee)

        # if order_filed:
        #     record_query = record_query.order_by(getattr(models.Employee, order_filed))

        record_query = record_query.filter(models.Employee)
        
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Employee.firstname.ilike('%' + str(keyword) + '%'),
                    models.Employee.email.ilike('%' + str(keyword) + '%'),
                    models.Employee.lastname.ilike('%' + str(keyword) + '%'),

                )
            )
        if status:
            record_query = record_query.filter(models.Employee.status == status)
        
        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.Employee.date_added.asc())
        
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.Employee.date_added.desc())

        if user_uuid:
            record_query = record_query.filter(models.Employee.uuid == user_uuid)

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.EmployeResponseList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )
    
employe = CRUDEmployee(models.Employee)
