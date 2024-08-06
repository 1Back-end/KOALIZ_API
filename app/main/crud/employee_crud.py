from datetime import datetime, timedelta,timezone
import math
from typing import Optional, Union
from pydantic import EmailStr
from sqlalchemy import or_
from app.main.core.i18n import __
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload,contains_eager 
from app.main import schemas, models
import uuid as py_uuid



class CRUDEmployee(CRUDBase[models.Employee,schemas.EmployeCreate,schemas.EmployeUpdate]):
    
    @classmethod
    def is_in_nursery_employees(cls,db:Session,employe_uuid:str,nursery_uuid:str):
        return db.query(models.Employee).join(models.NurseryEmployees).\
            filter(models.NurseryEmployees.nursery_uuid == nursery_uuid).\
                filter(models.NurseryEmployees.employee_uuid == employe_uuid).\
                    first()
    
    @classmethod
    def is_in_team_employees(cls,db:Session,employe_uuid:str,team_uuid:str):
        return db.query(models.Employee).join(models.TeamEmployees).\
            filter(models.TeamEmployees.team_uuid == team_uuid).\
                filter(models.TeamEmployees.employee_uuid == employe_uuid).\
                    first()
    
    @classmethod
    def get_by_uuids(cls, db: Session, uuids: list[str]) -> Optional[list[models.Employee]]:
        return db.query(models.Employee).filter(models.Employee.uuid.in_(uuids)).all()
    
    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Union[models.Employee, None]:
        return db.query(models.Employee).filter(models.Employee.uuid == uuid,models.Employee.status!="DELETED").first()
    
    @classmethod
    def create(cls, db: Session, obj_in: list[schemas.EmployeCreate]) -> list[models.Employee]:
        employees:list[models.Employee] =[]
        for obj in obj_in:
            
            db_obj = models.Employee(
                uuid= str(py_uuid.uuid4()),
                firstname = obj.firstname,
                lastname = obj.lastname,
                email = obj.email,
                avatar_uuid = obj.avatar_uuid if obj.avatar_uuid else None,
                status = obj.status
            )
            db.add(db_obj)
            db.flush()

            employees.append(db_obj)
            
            for nursery_uuid in obj.nursery_uuid_tab:
                nursery_employe = cls.is_in_nursery_employees(db, employe_uuid=db_obj.uuid, nursery_uuid=nursery_uuid)
                if not nursery_employe:
                    nursery_employe = models.NurseryEmployees(
                        uuid= str(py_uuid.uuid4()),
                        employee_uuid = db_obj.uuid,
                        nursery_uuid = nursery_uuid,
                        status = "ACTIVED"
                    )
                    db.add(nursery_employe)
                    db.flush()
            
            if obj.team_uuid_tab:
                for team_uuid in obj.team_uuid_tab:
                    team_member = cls.is_in_team_employees(db, employe_uuid=db_obj.uuid, team_uuid=team_uuid)
                    if not team_member:
                        team_member = models.TeamEmployees(
                            uuid= str(py_uuid.uuid4()),
                            employee_uuid = db_obj.uuid,
                            team_uuid = team_uuid,
                            status = "ACTIVED"
                        )
                        db.add(team_member)
                        db.flush()
        db.commit()
    
        return employees
    
    @classmethod
    def update(cls, db: Session,obj_in: schemas.EmployeUpdate) -> models.Employee:
        db_obj = cls.get_by_uuid(db, obj_in.uuid)
        db_obj.firstname = obj_in.firstname if obj_in.firstname else db_obj.firstname
        
        db_obj.lastname = obj_in.lastname if obj_in.lastname else db_obj.lastname
        db_obj.email = obj_in.email if obj_in.email else db_obj.email
        
        db_obj.avatar_uuid = obj_in.avatar_uuid if obj_in.avatar_uuid else db_obj.avatar_uuid
        db_obj.status = obj_in.status if obj_in.status else db_obj.status

        for nursery_uuid in obj_in.nursery_uuid_tab:
                nursery_employe = cls.is_in_nursery_employees(db, employe_uuid=db_obj.uuid, nursery_uuid=nursery_uuid)
                if not nursery_employe:
                    nursery_employe = models.NurseryEmployees(
                        uuid= str(py_uuid.uuid4()),
                        employee_uuid = db_obj.uuid,
                        nursery_uuid = nursery_uuid,
                    )
                    db.add(nursery_employe)
                    db.flush()

        if obj_in.team_uuid_tab:
            # teams = cls.get_by_uuids(db, obj_in.team_uuid_tab)
            for team_uuid in obj_in.team_uuid_tab:
                team_member = cls.is_in_team_employees(db, employe_uuid=obj_in.uuid, team_uuid=team_uuid)
                if not team_member:
                    team_members = models.TeamEmployees(
                        uuid= str(py_uuid.uuid4()),
                        employee_uuid = db_obj.uuid,
                        team_uuid = team_uuid
                    )
                    db.add(team_members)
                    db.flush()
        # db_obj.team_uuid = obj_in.team_uuid if obj_in.team_uuid else db_obj.team_uuid
        # db_obj.nursery_uuid = obj_in.nursery_uuid if obj_in.nursery_uuid else db_obj.nursery_uuid
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @classmethod
    def delete(cls,db:Session, uuid):
        administrator = cls.get_by_uuid(db, uuid)
        db.delete(administrator)
        db.commit()
    
    @classmethod
    def soft_delete(cls,db:Session, obj_in:list[schemas.EmployeDelete]):
        for obj in obj_in:
            db_obj = cls.get_by_uuid(db, obj.uuid)
            db_obj.status = models.EmployeStatusEnum.DELETED
            db.flush()

            if obj.nursery_uuid_tab:
                for nursery_uuid in obj.nursery_uuid_tab:
                    nursery_employe = cls.is_in_nursery_employees(db, employe_uuid=db_obj.uuid, nursery_uuid=nursery_uuid)
                    if nursery_employe:
                        nursery_employe.status = models.EmployeStatusEnum.DELETED
                        db.flush()
            
            if obj.team_uuid_tab:
                for team_uuid in obj.team_uuid_tab:
                    team_member = cls.is_in_team_employees(db, employe_uuid=db_obj.uuid, team_uuid=team_uuid)
                    if team_member:
                        team_member.status = models.EmployeStatusEnum.DELETED
                        db.flush()
                
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
        employee_uuid:Optional[str] = None,
        keyword:Optional[str]= None
        # order_filed:Optional[str] = None   
    ):
        record_query = db.query(models.Employee).\
            filter(models.Employee.status != models.EmployeStatusEnum.DELETED).\
                outerjoin(models.TeamEmployees, models.Employee.uuid == models.TeamEmployees.employee_uuid).\
                outerjoin(models.Team, models.TeamEmployees.team_uuid == models.Team.uuid).\
                    filter(models.Team.status != "DELETED").\
                        options(contains_eager(models.Employee.teams))

        # if order_filed:
        #     record_query = record_query.order_by(getattr(models.Employee, order_filed))

        
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

        if employee_uuid:
            record_query = record_query.filter(models.Employee.uuid == employee_uuid)

        total = record_query.count()
        print("total:",len(record_query.all()))
        print("total1:",total)
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.EmployeResponseList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )
    
employe = CRUDEmployee(models.Employee)
