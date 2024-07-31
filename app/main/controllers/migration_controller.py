import json
import os
import shutil
import platform
from dataclasses import dataclass
from typing import Any

from sqlalchemy.exc import ProgrammingError

from app.main import crud
from fastapi import APIRouter, Body, Depends, HTTPException
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import Column, String
from app.main import schemas
from app.main.core.config import Config
from app.main.core import dependencies
from app.main.core.security import get_password_hash
from app.main.models.db.base_class import Base
from app.main.utils import logger
from app.main import models, crud
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
        logger.info("Successfully created the directory %s " % migrations_folder)

    try:
        # Get the environment system
        if platform.system() == 'Windows':

            os.system('set PYTHONPATH=. && .\\venv\\Scripts\\python.exe -m alembic revision --autogenerate')
            os.system('set PYTHONPATH=. && .\\venv\\Scripts\\python.exe -m alembic upgrade head')

        else:
            os.system('PYTHONPATH=. alembic revision --autogenerate')
            os.system('PYTHONPATH=. alembic upgrade head')

        """ Try to remove previous alembic versions folder """
        try:
            shutil.rmtree(migrations_folder)
            pass
        except Exception as e:
            pass

        return {"message": "Les tables de base de données ont été créées avec succès"}

    except ProgrammingError as e:
        raise ProgrammingError(status_code=512, detail=str(e))
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
                    crud.role.update(db, schemas.RoleUpdate(**data))
                else:
                    user_role = models.Role(
                        title_fr=data["title_fr"],
                        title_en=data["title_en"],
                        code=data["code"],
                        group=data["group"],
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
    Create admins users.
    """
    check_user_access_key(admin_key)
    try:
        with open('{}/app/main/templates/default_data/administrator.json'.format(os.getcwd()), encoding='utf-8') as f:
            datas = json.load(f)
            for data in datas:
                db_obj = crud.administrator.get_by_uuid(db=db, uuid=data["uuid"])
                if db_obj:
                    crud.administrator.update(db, schemas.AdministratorUpdate(
                        uuid=data['uuid'],
                        firstname=data['firstname'],
                        lastname=data['lastname'],
                        email=data['email'],
                        role_uuid=data['role_uuid'],
                        avatar_uuid=data['avatar_uuid'],
                        otp=data['otp'],
                        otp_expired_at=data['otp_expired_at'],
                        otp_password=data['otp_password'],
                        otp_password_expired_at=data['otp_password_expired_at'],
                        password_hash=get_password_hash(data['password_hash']),
                        status=data['status'],
                        date_added=data['date_added'],
                        date_modified=data['date_modified']
                    )
                                              )
                else:
                    # crud.administrator.create(db,schemas.AdministratorCreate(**data))
                    db_obj = models.Administrator(
                        uuid=data["uuid"],
                        firstname=data["firstname"],
                        lastname=data["lastname"],
                        email=data['email'],
                        role_uuid=data["role_uuid"],
                        avatar_uuid=data["avatar_uuid"],
                        otp=data["otp"],
                        otp_expired_at=data["otp_expired_at"],
                        otp_password=data["otp_password"],
                        otp_password_expired_at=data["otp_password_expired_at"],
                        password_hash=get_password_hash(data["password_hash"]),
                        status=data["status"],
                        date_added=data["date_added"],
                        date_modified=data["date_modified"]
                    )
                    db.add(db_obj)
                    db.flush()
                    db.commit()
        return {"message": "Les administrateurs ont été créés avec succès"}

    except IntegrityError as e:
        logger.error(str(e))
        raise HTTPException(status_code=409, detail=__("admin-role-conflict"))
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="Erreur du serveur")


@router.post("/create-membership-types", response_model=schemas.Msg, status_code=201)
async def create_membershiptypes(
        db: Session = Depends(dependencies.get_db),
        admin_key: schemas.AdminKey = Body(...)
) -> dict[str, str]:
    """
    Create memberships.
    """
    check_user_access_key(admin_key)

    try:
        with open('{}/app/main/templates/default_data/membershiptype.json'.format(os.getcwd()), encoding='utf-8') as f:
            datas = json.load(f)

            for data in datas:
                print("data", data)
                db_obj = db.query(models.Membership).filter_by(uuid=data["uuid"]).first()
                if db_obj:
                    db_obj.title_en = data["title_en"]
                    db_obj.title_fr = data["title_fr"]
                    db_obj.description = data["description"]
                    # db_obj.price = data["price"]
                    db_obj.date_added = data["date_added"]
                    db_obj.date_modified = data["date_modified"]
                    db.commit()

                else:
                    # crud.administrator.create(db,schemas.AdministratorCreate(**data))
                    db_obj = models.Membership(
                        uuid=data["uuid"],
                        title_en=data["title_en"],
                        title_fr=data["title_fr"],
                        description=data["description"],
                        # price = data["price"],
                        date_added=data["date_added"],
                        date_modified=data["date_modified"]
                    )
                    db.add(db_obj)
                    db.commit()

        return {"message": "Les types d'adhésion ont été créés avec succès"}

    except IntegrityError as e:
        logger.error(str(e))
        raise HTTPException(status_code=409, detail=__("conflict"))
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="Erreur du serveur")


@router.post("/create-membership", response_model=schemas.Msg, status_code=201)
async def create_membership(
        db: Session = Depends(dependencies.get_db),
        admin_key: schemas.AdminKey = Body(...)
) -> dict[str, str]:
    """
    Create memberships.
    """
    check_user_access_key(admin_key)

    try:
        with open('{}/app/main/templates/default_data/membership.json'.format(os.getcwd()), encoding='utf-8') as f:
            datas = json.load(f)

            for data in datas:
                db_obj = crud.membership.get_by_uuid(db=db, uuid=data["uuid"])
                if db_obj:
                    db_obj.title_en = data["title_en"]
                    db_obj.title_fr = data["title_fr"]
                    db_obj.description = data["description"] if data["description"] else None

                    db_obj.status = data["status"]
                    db_obj.perido_unit = data["perido_unit"]
                    db_obj.period_from = data["period_from"]

                    db_obj.period_to = data["period_to"]
                    db_obj.duration = data["duration"]
                    db_obj.date_added = data["date_added"]
                    db_obj.date_modified = data["date_modified"]
                    db.commit()

                else:
                    # crud.administrator.create(db,schemas.AdministratorCreate(**data))
                    db_obj = models.Membership(
                        uuid=data["uuid"],
                        title_en=data["title_en"],
                        title_fr=data["title_fr"],
                        description=data["description"],
                        period_to=data["period_to"],
                        period_from=data["period_from"],
                        period_unit=data["period_unit"],
                        duration=data["duration"],
                        status=data["status"],
                        date_added=data["date_added"],
                        date_modified=data["date_modified"]
                    )
                    db.add(db_obj)
                    db.commit()
        return {"message": "Les abonnements ont été créés avec succès"}

    except IntegrityError as e:
        logger.error(str(e))
        raise HTTPException(status_code=409, detail=__("conflict"))
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="Erreur du serveur")
