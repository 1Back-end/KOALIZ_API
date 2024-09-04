from datetime import datetime, timedelta,timezone
import math
from typing import Optional, Union
from sqlalchemy import or_
from app.main.core.i18n import __
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload,contains_eager 
from app.main import schemas, models,crud
import uuid as py_uuid



class CRUDGroup(CRUDBase[models.Group, schemas.GroupCreate,schemas.GroupUpdate]):
    
    @classmethod
    def is_in_group_team(cls,db:Session,team_uuid:str,group_uuid:str):
        return db.query(models.GroupTeams).\
            filter(models.GroupTeams.team_uuid == team_uuid).\
                filter(models.GroupTeams.group_uuid == group_uuid).\
                    first()
    
    @classmethod
    def get_by_uuids(cls, db: Session, uuids: list[str]) -> Optional[list[models.Group]]:
        return db.query(models.Group).\
                filter(models.Group.uuid.in_(uuids)).\
                    all()
    
    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Union[models.Group, None]:
        return db.query(models.Group).filter(models.Group.uuid == uuid,models.Group.status!="DELETED").\
            first()
    
    @classmethod
    def create(cls, db: Session, obj_in: list[schemas.GroupCreate],added_by:models.Owner) -> list[models.Group]:
                
        group_list = [] 
        for obj in obj_in: 
            db_obj = models.Group(
                uuid= str(py_uuid.uuid4()),
                title_fr= obj.title_fr,
                title_en= obj.title_en,
                code = obj.code,
                description = obj.description,
                added_by_uuid = added_by.uuid
            )
            db.add(db_obj)
            db.commit()
            for team_uuid in obj.team_uuid_tab:
                group_team = crud.group.is_in_group_team(db,team_uuid,db_obj.uuid)
                print("group_team1234", group_team)
                if not group_team:
                    group_team = models.GroupTeams(
                        uuid= str(py_uuid.uuid4()),
                        group_uuid = db_obj.uuid,
                        team_uuid = team_uuid,
                    )
                    db.add(group_team)
                    db.commit()

        group_list.append(db_obj)
        db.refresh(db_obj)
    
        return group_list
    
    @classmethod
    def update(cls, db: Session,obj_in: schemas.GroupUpdate) -> models.Group:
        db_obj = cls.get_by_uuid(db, obj_in.uuid)
        
        db_obj.title_en = obj_in.title_en if obj_in.title_en else db_obj.title_en 
        db_obj.title_fr = obj_in.title_fr if obj_in.title_fr else db_obj.title_fr 
        db_obj.code = obj_in.code if obj_in.code else db_obj.code 
        
        db_obj.description = obj_in.description if obj_in.description else db_obj.description
        db.commit()
        for team_uuid in obj_in.team_uuid_tab:
            team_group = crud.group.is_in_group_team(db,team_uuid,db_obj.uuid)

            if not team_group:
                team_group = models.GroupTeams(
                uuid= str(py_uuid.uuid4()),
                team_uuid = team_uuid,
                group_uuid = db_obj.uuid,
                )
                db.add(team_group)
                db.commit()    

        db.refresh(db_obj)
        return db_obj
    
    @classmethod
    def soft_delete(cls,db:Session, uuids:list[str]):
        db_objs = cls.get_by_uuids(db, uuids)

        for db_obj in db_objs:
            db_obj.status = models.EmployeStatusEnum.DELETED
            db.commit()

    @classmethod
    def delete_team_from_group(cls,db:Session, obj_in:schemas.DeleteTeamFromGroup):
        exist_team_group = cls.is_in_group_team(db, obj_in)

        if exist_team_group and exist_team_group.status!= "DELETED":
            exist_team_group.status ="DELETED"
            db.commit()

    @classmethod
    def get_multi(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 30,
        order:Optional[str] = None,
        status:Optional[str] = None,
        group_uuid:Optional[str] = None,
        keyword:Optional[str]= None,
        # order_filed:Optional[str] = None   
    ):

        record_query = db.query(models.Group).\
            filter(models.Group.status !="DELETED").\
                outerjoin(models.GroupTeams,models.Group.uuid == models.GroupTeams.group_uuid).\
                outerjoin(models.Team, models.GroupTeams.team_uuid == models.Team.uuid).\
                    filter(models.Team.status!="DELETED").\
                        options(contains_eager(models.Group.teams))

        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Group.title_fr.ilike('%' + str(keyword) + '%'),
                    models.Group.title_en.ilike('%' + str(keyword) + '%'),
                    models.Group.code.ilike('%' + str(keyword) + '%'),
                    models.Group.description.ilike('%' + str(keyword) + '%'),

                )
            )
        if status:
            record_query = record_query.filter(models.Group.status == status)
        
        if order and order== "asc":
            record_query = record_query.order_by(models.Group.date_added.asc())
        
        elif order and order== "desc":
            record_query = record_query.order_by(models.Group.date_added.desc())

        if group_uuid:
            record_query = record_query.filter(models.Group.uuid == group_uuid)

        total = len(record_query.all())

        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.GroupResponseList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )
    
group = CRUDGroup(models.Group)





