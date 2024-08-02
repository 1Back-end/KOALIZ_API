from datetime import datetime, timedelta,timezone
import math
from typing import Optional, Union
from sqlalchemy import or_
from app.main.core.i18n import __
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload 
from app.main import schemas, models,crud
import uuid as py_uuid



class CRUDTeam(CRUDBase[models.Team, schemas.TeamCreate,schemas.TeamUpdate]):
    
    @classmethod
    def get_by_name(cls, db:Session, name:str)->models.Team:
        return db.query(models.Team).filter(models.Team.name == name).first()
    
    @classmethod
    def get_by_uuids(cls, db: Session, uuids: list[str]) -> Optional[list[models.Team]]:
        return db.query(models.Team).filter(models.Team.uuid.in_(uuids)).all()
    
    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Union[models.Team, None]:
        return db.query(models.Team).filter(models.Team.uuid == uuid,models.Team.status!="DELETED").first()
    
    @classmethod
    def create(cls, db: Session, obj_in: list[schemas.TeamCreate],owner_uuid:str) -> models.Team:

        for obj in obj_in: 
            db_obj = models.Team(
                uuid= str(py_uuid.uuid4()),
                name = obj.name,
                leader_uuid = obj.leader_uuid,
                description = obj.description,
                status = obj.status,
                owner_uuid = owner_uuid
            )
            db.add(db_obj)
            db.flush()

            member_uuid_tab = list(set(obj.member_uuid_tab + [obj.leader_uuid]))
            for member_uuid in member_uuid_tab:
                team_members = crud.employe.is_in_team_employees(db,member_uuid,db_obj.uuid)
                if not team_members:
                    team_members = models.TeamEmployees(
                        uuid= str(py_uuid.uuid4()),
                        employee_uuid = member_uuid,
                        team_uuid = db_obj.uuid,
                        status = obj.status

                    )
                    db.add(team_members)
                    db.flush()

        db.commit()
        db.refresh(db_obj)
    
        return db_obj
    
    @classmethod
    def update(cls, db: Session,obj_in: schemas.TeamUpdate) -> models.Team:
        db_obj = cls.get_by_uuid(db, obj_in.uuid)
        
        db_obj.name = obj_in.name 
        db_obj.leader_uuid = obj_in.leader_uuid
        
        db_obj.status = obj_in.status  
        db_obj.description = obj_in.description if obj_in.description else db_obj.description

        db.flush()
        
        member_uuid_tab = list(set(obj_in.member_uuid_tab + [obj_in.leader_uuid]))
        for member_uuid in member_uuid_tab:
            team_member = crud.employe.is_in_team_employees(db,member_uuid,db_obj.uuid)

            if not team_member:
                team_member = models.TeamEmployees(
                uuid= str(py_uuid.uuid4()),
                employee_uuid = member_uuid,
                team_uuid = db_obj.uuid,
                status = "ACTIVED"
            )
                db.add(team_member)
                db.flush()

        db.commit()    
        db.refresh(db_obj)
        
        return db_obj
    
    @classmethod
    def soft_delete(cls,db:Session, uuids:list[str]) -> models.Team:
        db_objs = cls.get_by_uuids(db, uuids)

        for db_obj in db_objs:
            db_obj.status = models.EmployeStatusEnum.DELETED
        db.commit()
    
    
    @classmethod
    def get_multi(
        *,
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 30,
        order:Optional[str] = None,
        status:Optional[str] = None,
        user_uuid:Optional[str] = None,
        keyword:Optional[str]= None,
        owner_uuid: str
        # order_filed:Optional[str] = None   
    ):
        record_query = db.query(models.Team).\
            filter(models.Team.owner_uuid == owner_uuid)

        # if order_filed:
        #     record_query = record_query.order_by(getattr(models.Team, order_filed))
        
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Team.name.ilike('%' + str(keyword) + '%'),
                    models.Team.description.ilike('%' + str(keyword) + '%'),

                )
            )
        if status:
            record_query = record_query.filter(models.Team.status == status)
        
        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.Team.date_added.asc())
        
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.Team.date_added.desc())

        if user_uuid:
            record_query = record_query.filter(models.Team.uuid == user_uuid)

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.TeamResponseList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )
    
team = CRUDTeam(models.Team)





