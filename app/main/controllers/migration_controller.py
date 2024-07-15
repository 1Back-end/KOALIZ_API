import json
import os
import shutil
import platform
from dataclasses import dataclass
from typing import Any
from app.main import crud
from fastapi import APIRouter, Body, Depends, HTTPException
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import Column, String
from app.main import schemas
from app.main.core.config import Config
from app.main.core import dependencies
from app.main.models.db.base_class import Base
from app.main.utils import logger
from app.main import models,crud
from app.main.core.i18n import __

router = APIRouter(prefix="/migrations", tags=["migrations"])


def check_user_access_key(admin_key: schemas.AdminKey):
    logger.info(f"Check user access key: {admin_key.key}")
    if admin_key.key not in [Config.ADMIN_KEY]:
        raise HTTPException(status_code=400, detail="Clé d'accès incorrecte")


@router.post("/create-database-tables", response_model=schemas.Msg, status_code=201)
async def create_database_tables(
        db: Session = Depends(dependencies.get_db),
        admin_key: schemas.AdminKey = Body(...)
) -> dict[str, str]:
    """
    Create database structure (tables)
    """
    check_user_access_key(admin_key)
    """ Try to remove previous alembic tags in database """
    try:
        @dataclass
        class AlembicVersion(Base):
            __tablename__ = "alembic_version"
            version_num: str = Column(String(32), primary_key=True, unique=True)

        db.query(AlembicVersion).delete()
        db.commit()
    except Exception as e:
        pass

    """ Try to remove previous alembic versions folder """
    migrations_folder = os.path.join(os.getcwd(), "alembic", "versions")
    try:
        shutil.rmtree(migrations_folder)
    except Exception as e:
        pass

    """ create alembic versions folder content """
    try:
        os.mkdir(migrations_folder)
    except OSError:
        logger.error("Creation of the directory %s failed" % migrations_folder)
    else:
        logger.error("Successfully created the directory %s " % migrations_folder)

    try:
        # Get the environment system
        if platform.system() == 'Windows':

            os.system('set PYTHONPATH=. && .\\.venv\Scripts\python.exe -m alembic revision --autogenerate')

        else:
            os.system('PYTHONPATH=. alembic revision --autogenerate')

        # Get the environment system
        if platform.system() == 'Windows':

            os.system('set PYTHONPATH=. && .\\.venv\Scripts\python.exe -m alembic upgrade head')

        else:
            os.system('PYTHONPATH=. alembic upgrade head')

        """ Try to remove previous alembic versions folder """
        try:
            shutil.rmtree(migrations_folder)
            pass
        except Exception as e:
            pass

        return {"message": "Les tables de base de données ont été créées avec succès"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/create-user-roles", response_model=schemas.Msg, status_code=201)
async def create_user_roles(
        db: Session = Depends(dependencies.get_db),
        admin_key: schemas.AdminKey = Body(...)
) -> dict[str, str]:
    """
    Create user roles.
    """
    check_user_access_key(admin_key)
    
    try:
        with open('{}/app/main/templates/default_data/roles.json'.format(os.getcwd()), encoding='utf-8') as f:        
            datas = json.load(f)
        
            for data in datas:
                user_role = crud.role.get_by_uuid(db=db, uuid=data["uuid"])
                if user_role:
                    crud.role.update(db,schemas.RoleUpdate(**data))
                else:
                    user_role = models.Role(
                        title_fr=data["title_fr"],
                        title_en=data["title_en"],
                        code=data["code"],
                        group = data["group"],
                        description=data["description"],
                        uuid=data["uuid"]
                    )
                    db.add(user_role)
                    db.commit()
        return {"message": "Les rôles ont été créés avec succès"}
        
    except IntegrityError as e:
        logger.error(str(e))
        raise HTTPException(status_code=409, detail=__("user-role-conflict"))
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="Erreur du serveur")

@router.post("/create-admin-users", response_model=schemas.Msg, status_code=201)
async def create_admin_users(
        db: Session = Depends(dependencies.get_db),
        admin_key: schemas.AdminKey = Body(...)
) -> dict[str, str]:
    """
    Create user roles.
    """
    check_user_access_key(admin_key)
    
    try:
        with open('{}/app/main/templates/default_data/administrator.json'.format(os.getcwd()), encoding='utf-8') as f:        
            datas = json.load(f)
        
            for data in datas:
                db_obj = crud.administrator.get_by_uuid(db=db, uuid=data["uuid"])
                if db_obj:
                    crud.administrator.update(db,schemas.AdministratorUpdate(
                        uuid = data['uuid'],
                        firstname = data['firstname'],
                        lastname = data['lastname'],
                        email =data['email'],
                        role_uuid = data['role_uuid'],
                        avatar_uuid =data['avatar_uuid'],
                        otp = data['otp'],
                        otp_expired_at = data['otp_expired_at'],
                        otp_password =data['otp_password'],
                        otp_password_expired_at =data['otp_password_expired_at'],
                        password_hash =data['password_hash'],
                        status= data['status'],
                        date_added = data['date_added'],
                        date_modified = data['date_modified']
                    )
                    )
                else:
                    # crud.administrator.create(db,schemas.AdministratorCreate(**data))
                    db_obj = models.Administrator(
                        uuid = data["uuid"],
                        firstname = data["firstname"],
                        lastname = data["lastname"],
                        email =data['email'],
                        role_uuid = data["role_uuid"],
                        avatar_uuid =data["avatar_uuid"],
                        otp = data["otp"],
                        otp_expired_at =data["otp_expired_at"],
                        otp_password =data["otp_password"],
                        otp_password_expired_at = data["otp_password_expired_at"],
                        password_hash = data["password_hash"],
                        status= data["status"],
                        date_added = data["date_added"],
                        date_modified = data["date_modified"]
                    )
                    db.add(db_obj)
                    db.commit()
        return {"message": "Les administrateurs ont été créés avec succès"}
        
    except IntegrityError as e:
        logger.error(str(e))
        raise HTTPException(status_code=409, detail=__("admin-role-conflict"))
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="Erreur du serveur")
