from datetime import datetime, timedelta,timezone
import math
from typing import Optional
from sqlalchemy import or_
from app.main.core.i18n import __
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload 
from app.main import schemas, models
import uuid



class CRUDTag(CRUDBase[models.Tags, schemas.TagCreate,schemas.TagUpdate]):
    
    @classmethod
    def get_title(cls,db:Session, title_fr:str,title_en:str):
        print(f"yo-1 title_fr{title_fr},title_en:{title_en}",title_fr,title_en)
        return db.query(models.Tags).filter(
            or_(
                models.Tags.title_fr == title_fr,
                models.Tags.title_en == title_en
            )
        ).first()
    
    @classmethod
    def create(cls, db: Session,obj_in: schemas.TagCreate) -> models.Tags:
        tag = models.Tags(
            uuid=str(uuid.uuid4()),
            title_fr=obj_in.title_fr,
            title_en=obj_in.title_en,
            color=obj_in.color,
            icon_uuid=obj_in.icon_uuid,
            type=obj_in.type,
            # element_uuid=obj_in.element_uuid
            # elemntype=obj= obj_in.elemntype
        )
        db.add(tag)
        db.flush()
        
        tag_element:models.TagElement = models.TagElement(
            uuid=str(uuid.uuid4()),
            tag_uuid=tag.uuid,
            element_uuid=obj_in.element_uuid,
            element_type=tag.type
            # element_type=obj_in.elemntype

        )
        db.add(tag_element)
        db.commit()
        db.refresh(tag)
        return tag
    
    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Optional[models.Tags]:
        return db.query(models.Tags).filter(models.Tags.uuid == uuid).first()
    
    @classmethod
    def get_by_uuids(cls, db: Session, uuids: list[str]) -> Optional[list[models.Tags]]:
        return db.query(models.Tags).filter(models.Tags.uuid.in_(uuids)).all
    
    @classmethod
    def update(cls, db: Session, obj_in: schemas.TagUpdate) -> models.Tags:
        tag = cls.get_by_uuid(db, obj_in.uuid)
        tag.title_fr = obj_in.title_fr if obj_in.title_fr else tag.title_fr
        tag.title_en = obj_in.title_en if obj_in.title_en else tag.title_en
        tag.color = obj_in.color if obj_in.color else tag.color
        tag.icon_uuid = obj_in.icon_uuid if obj_in.icon_uuid else tag.icon_uuid
        tag.type = obj_in.type if obj_in.type else tag.type
        db.commit()
        db.refresh(tag)
        return tag
    
    @classmethod
    def delete(cls, db: Session, uuids:list[str]) -> None:
        db.query(models.Tags).filter(models.Tags.uuid.in_(uuids)).delete()
        db.commit()
    
    
    
    @classmethod
    def get_by_name(cls, db: Session, name: str) -> Optional[models.Tags]:
        return db.query(models.Tags).filter(
            or_(models.Tags.title_fr == name, models.Tags.title_en == name)
        ).first()
    
    @classmethod
    def get_by_type(cls, db: Session, tag_type: str) -> Optional[models.Tags]:
        return db.query(models.Tags).filter(models.Tags.type == tag_type).all()
    
    
    
    @classmethod
    def get_multi(
        cls, 
        db: Session, 
        page: int = 1, 
        per_page: int = 30, 
        order: Optional[str] = None, 
        title: Optional[str] = None,
        color: Optional[str] = None,
        type: Optional[str] = None,
        icon_uuid:Optional[str]= None
        ):
        
        record_query = db.query(models.Tags).options(
            joinedload(models.Tags.icon)
        )
        
        if title:
            record_query = record_query.filter(
                or_(
                    models.Tags.title_fr.ilike(f"%{title}%"), 
                    models.Tags.title_en.ilike(f"%{title}%")
                    )
            )

        if color:
            record_query = record_query.filter(models.Tags.type.ilike(color))
        
        if icon_uuid:
            record_query = record_query.filter(models.Tags.icon_uuid==icon_uuid)
        
        if type:
            record_query = record_query.filter(models.Tags.type.ilike(type))
        total = record_query.count()

        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.Administrator.date_added.asc())
        
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.Administrator.date_added.desc())

        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.TagsResponseList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page = page,
            data = record_query
        )




tag = CRUDTag(models.Tags)
