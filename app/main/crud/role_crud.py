from datetime import datetime, timedelta
from typing import Union, Optional, List
from app.main.core.i18n import __
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session
from app.main import schemas, models
import uuid


class CRUDRole(CRUDBase[models.Role, schemas.RoleCreate,schemas.RoleUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Union[models.Role, None]:
        return db.query(models.Role).filter(models.Role.uuid == uuid).first()
    
    @classmethod
    def get_by_code(cls, db: Session, code: str) -> Union[models.Role, None]:
        return db.query(models.Role).filter(models.Role.code == code).first()
    
    @classmethod
    def get_by_group(cls, db: Session) -> List[models.Role]:
        return db.query(models.Role).all()
    
    @classmethod
    def create(cls, db: Session, obj_in: schemas.RoleCreate) -> models.Role:
        role = models.Role(
            uuid= str(uuid.uuid4()),
            title_fr=obj_in.title_fr,
            title_en=obj_in.title_en,
            code=obj_in.code,
            group = obj_in.group,
            description=obj_in.description
        )
    
        
        db.add(role)
        db.commit()
        db.refresh(role)
        return role
    
    @classmethod
    def update(cls, db: Session,obj_in: schemas.RoleUpdate) -> models.Role:
        role = cls.get_by_uuid(db, obj_in.uuid)
        role.title_fr = obj_in.title_fr if obj_in.title_fr else role.title_fr
        role.title_en = obj_in.title_en if obj_in.title_en else role.title_en
        role.code = obj_in.code if obj_in.code else role.code
        role.group = obj_in.group if obj_in.group else role.group  # not updateable field, so it remains the same.  # for example, if you want to update group, you should create a new role with new group and delete the old one.  # this is just a sample.  # in real world, you should consider the impact on existing users and data.  # it is not recommended to update group field.  # if you need
        role.description = obj_in.description if obj_in.description else role.description
        db.commit()
        db.refresh(role)
        return role
    
role = CRUDRole(models.Role)


