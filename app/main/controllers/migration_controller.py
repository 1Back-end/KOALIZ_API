from datetime import datetime, timedelta
import json
import os
import shutil
import platform
from dataclasses import dataclass
from typing import Any
import uuid

from sqlalchemy.exc import ProgrammingError

from app.main import crud
from fastapi import APIRouter, Body, Depends, HTTPException, BackgroundTasks
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import Column, String
from app.main import schemas
from app.main.core.config import Config
from app.main.core import dependencies
from app.main.core.security import get_password_hash
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
        logger.info("Successfully created the directory %s " % migrations_folder)

    try:
        # Get the environment system
        if platform.system() == 'Windows':

            os.system('set PYTHONPATH=. && .\\venv\Scripts\python.exe -m alembic revision --autogenerate')
            os.system('set PYTHONPATH=. && .\\venv\Scripts\python.exe -m alembic upgrade head')

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
    Create admins users.
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
                        password_hash =get_password_hash(data['password_hash']),
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
                        password_hash = get_password_hash(data["password_hash"]),
                        status= data["status"],
                        date_added = data["date_added"],
                        date_modified = data["date_modified"]
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
                print("data",data)
                db_obj = db.query(models.Membership).filter_by(uuid = data["uuid"]).first()
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
                        uuid = data["uuid"],
                        title_en = data["title_en"],
                        title_fr = data["title_fr"],
                        description = data["description"],
                        # price = data["price"],
                        date_added = data["date_added"],
                        date_modified = data["date_modified"]
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
                        uuid = data["uuid"],
                        title_en = data["title_en"],
                        title_fr = data["title_fr"],
                        description = data["description"],
                        period_to = data["period_to"],
                        period_from = data["period_from"],
                        period_unit = data["period_unit"],
                        duration = data["duration"],
                        status = data["status"],
                        date_added = data["date_added"],
                        date_modified = data["date_modified"]
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
    
@router.post("/create-meeting-types", response_model=schemas.Msg, status_code=201)
async def create_meeting_types(
        db: Session = Depends(dependencies.get_db),
        admin_key: schemas.AdminKey = Body(...)
) -> dict[str, str]:
    """
    Create meeting types.
    """
    check_user_access_key(admin_key)
    
    try:
        with open('{}/app/main/templates/default_data/meetingtype.json'.format(os.getcwd()), encoding='utf-8') as f:        
            datas = json.load(f)
        
            for data in datas:
                db_obj = db.query(models.MeetingType).filter_by(uuid = data["uuid"]).first()
                if db_obj:
                    db_obj.title_en = data["title_en"]
                    db_obj.title_fr = data["title_fr"]
                    db.commit()
                    
                else:
                    # crud.administrator.create(db,schemas.AdministratorCreate(**data))
                    db_obj = models.MeetingType(
                        uuid = data["uuid"],
                        title_en = data["title_en"],
                        title_fr = data["title_fr"]
                    )
                    db.add(db_obj)
                    db.commit()
        return {"message": "Les types de rencontre ont été créés avec succès"}
        
    except IntegrityError as e:
        logger.error(str(e))
        raise HTTPException(status_code=409, detail=__("conflict"))
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="Erreur du serveur")

@router.post("/create-activity-reminder-types", response_model=schemas.Msg, status_code=201)
async def create_activity_reminder_types(
        db: Session = Depends(dependencies.get_db),
        admin_key: schemas.AdminKey = Body(...)
) -> dict[str, str]:
    """
    Create meeting types.
    """
    check_user_access_key(admin_key)
    
    try:
        with open('{}/app/main/templates/default_data/activityremindertype.json'.format(os.getcwd()), encoding='utf-8') as f:        
            datas = json.load(f)
        
            for data in datas:
                db_obj = db.query(models.ActivityReminderType).filter_by(uuid = data["uuid"]).first()
                if db_obj:
                    db_obj.title_en = data["title_en"]
                    db_obj.title_fr = data["title_fr"]
                    db.commit()
                    
                else:
                    # crud.administrator.create(db,schemas.AdministratorCreate(**data))
                    db_obj = models.ActivityReminderType(
                        uuid = data["uuid"],
                        title_en = data["title_en"],
                        title_fr = data["title_fr"]
                    )
                    db.add(db_obj)
                    db.commit()
        return {"message": "Les types de rappel d'activité ont été créés avec succès"}

    except IntegrityError as e:
        logger.error(str(e))
        raise HTTPException(status_code=409, detail=__("conflict"))
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="Erreur du serveur")
    

def populate_data(db, start_year=2024, end_year=2024):

    for year in range(start_year, end_year + 1):
        # Créer une instance de Year
        year_obj = db.query(models.Year).filter(models.Year.year==year).first()
        if not year_obj:
            year_obj = models.Year(uuid=str(uuid.uuid4()), year=year)
            db.add(year_obj)
            db.commit()

        # Créer des mois pour l'année
        for month in range(1, 13):
            start_date = datetime(year, month, 1).date()
            if month == 12:
                end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)

            month_obj = db.query(models.Month).\
                filter(models.Month.start_date==start_date).\
                filter(models.Month.end_date==end_date).\
                filter(models.Month.year_uuid==year_obj.uuid).\
                first()
            if not month_obj:
                month_obj = models.Month(
                    uuid=str(uuid.uuid4()),
                    start_date=start_date,
                    end_date=end_date,
                    year_uuid=year_obj.uuid
                )
                db.add(month_obj)
                db.commit()

            # Créer des semaines pour chaque mois
            current_date = start_date
            while current_date <= end_date:
                week_start = current_date
                days_ahead = 6 - week_start.weekday() if week_start.weekday() <= 6 else 0
                week_end = week_start + timedelta(days=days_ahead)
                if week_end > end_date:
                    week_end = end_date

                week_obj = db.query(models.Week).\
                    filter(models.Week.start_date==week_start).\
                    filter(models.Week.end_date==week_end).\
                    filter(models.Week.month_uuid==month_obj.uuid).\
                    first()
                if not week_obj:
                    week_obj = models.Week(
                        uuid=str(uuid.uuid4()),
                        start_date=week_start,
                        end_date=week_end,
                        week_index=week_start.isocalendar()[1],
                        month_uuid=month_obj.uuid
                    )
                    db.add(week_obj)
                    db.commit()

                # Créer des jours pour chaque semaine
                day = week_start
                print("day: ",day)
                print("week_end: ",week_end)
                while day <= week_end:
                    day_obj = db.query(models.Day).\
                        filter(models.Day.day==day).\
                        filter(models.Day.month_uuid==month_obj.uuid).\
                        filter(models.Day.year_uuid==year_obj.uuid).\
                        filter(models.Day.week_uuid==week_obj.uuid).\
                        first()
                    if not day_obj:
                        day_obj = models.Day(
                            uuid=str(uuid.uuid4()),
                            day=day,
                            day_of_week=day.strftime('%A'),
                            month_uuid=month_obj.uuid,
                            year_uuid=year_obj.uuid,
                            week_uuid=week_obj.uuid
                        )
                        db.add(day_obj)
                        day += timedelta(days=1)

                        db.commit()
                # Passer à la semaine suivante
                current_date = week_end + timedelta(days=1)

@router.post("/create-default-planning-data", response_model=schemas.Msg, status_code=201)
async def create_default_planning_data(
    *,
    db: Session = Depends(dependencies.get_db),
    admin_key: schemas.AdminKey = Body(...),
    background_tasks: BackgroundTasks
) -> dict[str, str]:

    """ Remplit les tables avec des données pour les années spécifiées. """

    check_user_access_key(admin_key)

    try:
        start_year = 2024
        end_year = 2100

        background_tasks.add_task(populate_data, db, start_year, end_year)

        return {"message": "Les donnees par defaut ont été créés avec succès"}

    except IntegrityError as e:
        logger.error(str(e))
        raise HTTPException(status_code=409, detail=__("conflict"))
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="Erreur du serveur")
