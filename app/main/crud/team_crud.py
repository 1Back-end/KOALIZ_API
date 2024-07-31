from datetime import datetime, timedelta,timezone
import math
from typing import Optional, Union
from sqlalchemy import or_
from app.main.core.i18n import __
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload 
from app.main import schemas, models
import uuid as py_uuid



class CRUDTeam(CRUDBase[models.Team, schemas.TeamCreate,schemas.TeamUpdate]):
    
    @classmethod
    def get_by_uuids(cls, db: Session, uuids: list[str]) -> Optional[list[models.Team]]:
        return db.query(models.Team).filter(models.Team.uuid.in_(uuids)).all()
    
    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Union[models.Team, None]:
        return db.query(models.Team).filter(models.Team.uuid == uuid).first()
    
    @classmethod
    def create(cls, db: Session, obj_in: schemas.TeamCreate) -> models.Team:
        db_obj = models.Team(
            uuid= str(py_uuid.uuid4()),
            name = obj_in.name,
            team_uuid = obj_in.team_uuid,
            leader_uuid = obj_in.leader_uuid,
            description = obj_in.description,
            status = obj_in.status,
        )
        db.add(db_obj)
        db.flush()

        for member_uuid in obj_in.member_uuid_tab:
            team_members = models.TeamEmployees(
                uuid= str(py_uuid.uuid4()),
                employee_uuid = member_uuid,
                team_uuid = db_obj.uuid

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
        team_members = cls.get_by_uuids(db, obj_in.member_uuid_tab)
        for member in team_members:
            if not member in team_members:
                team_members = models.TeamEmployees(
                uuid= str(py_uuid.uuid4()),
                employee_uuid = member.uuid,
                team_uuid = db_obj.uuid

            )
            db.add(team_members)
            db.flush()
        db.commit()    
        db.refresh(db_obj)
        
        return db_obj
    
    @classmethod
    def soft_delete(cls,db:Session, uuids:list[str]) -> models.Team:
        db_obj = cls.get_by_uuid(db, uuids)
        db_obj.status = models.TeamStatusEnum
        db.commit()
    
    
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
        record_query = db.query(models.Team)

        # if order_filed:
        #     record_query = record_query.order_by(getattr(models.Team, order_filed))

        record_query = record_query.filter(models.Team)
        
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Team.firstname.ilike('%' + str(keyword) + '%'),
                    models.Team.email.ilike('%' + str(keyword) + '%'),
                    models.Team.lastname.ilike('%' + str(keyword) + '%'),

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





