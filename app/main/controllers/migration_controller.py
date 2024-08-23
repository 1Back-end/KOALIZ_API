from datetime import datetime, timedelta
import json
import os
import shutil
import platform
from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import uuid4
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

    except ProgrammingError as e:
        raise ProgrammingError(status_code=512, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/create-activity",response_model=schemas.Msg,status_code=201)
async def create_activity(
    db: Session = Depends(dependencies.get_db),
    admin_key: schemas.AdminKey = Body(...)
)-> dict[str, str]:
    """ Create a new activity """
    check_user_access_key(admin_key)
    try:
        with open('{}/app/main/templates/default_data/activity.json'.format(os.getcwd()), encoding='utf-8') as f:
            datas = json.load(f)
            
            for data in datas:
                activity = crud.activity.get_activity_by_uuid(db=db, uuid=data["uuid"])
                if activity:
                    crud.activity.update(db, schemas.ActivityUpdate(**data))
                else:
                    activity = models.Activity(
                        name_fr=data["name_fr"],
                        name_en=data["name_en"],
                        uuid=data["uuid"]
                    )
                    db.add(activity)
                    db.commit()
                    db.refresh(activity)
        return {"message": "Les activitées ont été créés avec succès"}
    except IntegrityError as e:
        logger.error(str(e))
        raise HTTPException(status_code=409, detail=__("conflict"))
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="Erreur du serveur")
    


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
                        status=data['status']
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
                        status=data["status"]
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
                db_obj = crud.membership.get_by_uuid(db=db, obj_uuid=data["uuid"])
                if db_obj:
                    #db_obj.title_en = data["title_en"]
                    #db_obj.title_fr = data["title_fr"]
                    #   db_obj.description = data["description"] if data["description"] else None
                    
                    db_obj.status = data["status"]
                    db_obj.period_unit = data["perido_unit"]
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


@router.post("/create-nursery-holidays", response_model=schemas.Msg, status_code=201)
async def create_user_roles(
        db: Session = Depends(dependencies.get_db),
        admin_key: schemas.AdminKey = Body(...)
) -> dict[str, str]:

    check_user_access_key(admin_key)

    for holiday_day in [
        {"month": 12, "day":  25, "name_fr": "Noël", "name_en": "Christmas"},
        {"month": 1,  "day": 1, "name_fr": "Jour de l'an", "name_en": "New Year's Day"},
        {"month": 8,  "day": 15, "name_fr": "Assomption", "name_en": "Assumption of Mary"},
    ]:
        for nursery in db.query(models.Nursery).filter(models.Nursery.status != models.NurseryStatusType.DELETED).all():
            nh = db.query(models.NuseryHoliday).filter(models.NuseryHoliday.day == holiday_day["day"]).filter(
                models.NuseryHoliday.month == holiday_day["month"]).filter(
                models.NuseryHoliday.nursery_uuid == nursery.uuid).first()
            if not nh:
                nh = models.NuseryHoliday(
                    uuid = str(uuid4()),
                    name_fr=holiday_day["name_fr"],
                    name_en=holiday_day["name_en"],
                    day=holiday_day["day"],
                    month=holiday_day["month"],
                    is_active=True,
                    nursery_uuid=nursery.uuid
                )
                db.add(nh)
            else:
                nh.name_fr = holiday_day["name_fr"]
                nh.name_en = holiday_day["name_en"]
    db.commit()

    return {"message": "Nurseries holidays created successfully"}


@router.post("/create-quote-settings", response_model=schemas.Msg, status_code=201)
async def create_user_roles(
        db: Session = Depends(dependencies.get_db),
        admin_key: schemas.AdminKey = Body(...)
) -> dict[str, str]:

    check_user_access_key(admin_key)

    default_quote = {
        "uuid": "2bee8286-5fe7-48bd-b93d-b7f20a32b47d",
        "adaptation_type": models.AdaptationType.PACKAGE,
        "adaptation_package_costs": 80,
        "adaptation_package_days": 6,
        "adaptation_hourly_rate": 0,
        "adaptation_hours_number": 0,
        "has_deposit": True,
        "deposit_type": models.DepositType.PERCENTAGE,
        "deposit_percentage": 30,
        "deposit_value": 0,
        "has_registration_fee": True,
        "registration_fee": 90,
        "last_special_month": True,
        "min_days_for_last_special_month": 5,
        "invoicing_time": models.InvoiceTimeType.END_OF_MONTH,
        "is_default": True
    }
    quote = db.query(models.QuoteSetting).filter(models.QuoteSetting.uuid==default_quote["uuid"]).first()
    if not quote:
        quote = models.QuoteSetting(
            uuid=default_quote["uuid"],
            adaptation_type=default_quote["adaptation_type"],
            adaptation_package_costs=default_quote["adaptation_package_costs"],
            adaptation_package_days=default_quote["adaptation_package_days"],
            adaptation_hourly_rate=default_quote["adaptation_hourly_rate"],
            adaptation_hours_number=default_quote["adaptation_hours_number"],
            has_deposit=default_quote["has_deposit"],
            deposit_type=default_quote["deposit_type"],
            deposit_percentage=default_quote["deposit_percentage"],
            deposit_value=default_quote["deposit_value"],
            has_registration_fee=default_quote["has_registration_fee"],
            registration_fee=default_quote["registration_fee"],
            last_special_month=default_quote["last_special_month"],
            min_days_for_last_special_month=default_quote["min_days_for_last_special_month"],
            invoicing_time=default_quote["invoicing_time"],
            is_default=default_quote["is_default"]
        )
        db.add(quote)
    else:
        quote.adaptation_type = default_quote["adaptation_type"]
        quote.adaptation_package_costs = default_quote["adaptation_package_costs"]
        quote.adaptation_package_days = default_quote["adaptation_package_days"]
        quote.adaptation_hourly_rate = default_quote["adaptation_hourly_rate"]
        quote.adaptation_hours_number = default_quote["adaptation_hours_number"]
        quote.has_deposit = default_quote["has_deposit"]
        quote.deposit_type = default_quote["deposit_type"]
        quote.deposit_percentage = default_quote["deposit_percentage"]
        quote.deposit_value = default_quote["deposit_value"]
        quote.has_registration_fee = default_quote["has_registration_fee"]
        quote.registration_fee = default_quote["registration_fee"]
        quote.last_special_month = default_quote["last_special_month"]
        quote.min_days_for_last_special_month = default_quote["min_days_for_last_special_month"]
        quote.invoicing_time = default_quote["invoicing_time"]
        quote.is_default = default_quote["is_default"]

    for hr in [
        {"uuid": "65ecdd63-0d32-4ea1-8169-99427775e0b1", "nb_days": 1, "nb_hours": 10, "hourly_rate": 10},
        {"uuid": "c6fecfcd-0857-4b6b-a755-b483cb7f57cc", "nb_days": 2, "nb_hours": 20, "hourly_rate": 10},
        {"uuid": "ff3231ad-b428-4d8c-b461-03849f4017c4", "nb_days": 3, "nb_hours": 30, "hourly_rate": 10},
        {"uuid": "b7e895b8-529b-416d-9afd-c29b531c9b8f", "nb_days": 4, "nb_hours": 40, "hourly_rate": 9.2},
        {"uuid": "13461ae6-5127-45ab-b1c6-779543a12825", "nb_days": 5, "nb_hours": 50, "hourly_rate": 8.7},
    ]:
        hrr = db.query(models.HourlyRateRange).filter(models.HourlyRateRange.uuid == hr["uuid"]).first()
        if not hrr:
            hrr = models.HourlyRateRange(
                uuid=hr["uuid"],
                number_of_day=hr["nb_days"],
                number_of_hours=hr["nb_hours"],
                hourly_rate=hr["hourly_rate"],
                quote_setting_uuid=quote.uuid
            )
        else:
            hrr.number_of_day = hr["nb_days"]
            hrr.number_of_hours = hr["nb_hours"]
            hrr.hourly_rate = hr["hourly_rate"]
            hrr.quote_setting_uuid = quote.uuid
        db.add(hrr)
    db.commit()

    return {"message": "Default quote setting created successfully"}

@router.post("/create-cmg-amount-range", response_model=schemas.Msg, status_code=201)
async def create_user_roles(
        db: Session = Depends(dependencies.get_db),
        admin_key: schemas.AdminKey = Body(...)
) -> dict[str, str]:
    check_user_access_key(admin_key)

    for cmg_a_r_item in [
        {"uuid": "4dd3d890-b8eb-4f39-8af0-962ec6857b3c", "lower": 22809, "upper": 50686, "family_type": models.FamilyType.COUPLE, "number_children": 1},
        {"uuid": "ab352375-0f21-4f35-bc4a-65720b6ebb6e", "lower": 26046, "upper": 57881, "family_type": models.FamilyType.COUPLE, "number_children": 2},
        {"uuid": "8ca7701f-fa43-4532-8028-466e59c545ff", "lower": 29283, "upper": 65076, "family_type": models.FamilyType.COUPLE, "number_children": 3},
        {"uuid": "fb0b54ae-0d67-472d-a359-4ae18f5591d3", "lower": 32520, "upper": 72271, "family_type": models.FamilyType.COUPLE, "number_children": 4},

        {"uuid": "4a65b981-db60-4072-b966-0a80853bd891", "lower": 31933, "upper": 70960, "family_type": models.FamilyType.SINGLE_PARENT, "number_children": 1},
        {"uuid": "538ab79e-d9b8-4daf-aa5c-076c424b4c3d", "lower": 36465, "upper": 81033, "family_type": models.FamilyType.SINGLE_PARENT, "number_children": 2},
        {"uuid": "87439690-91a2-45d3-9299-0924508b4d64", "lower": 40997, "upper": 91106, "family_type": models.FamilyType.SINGLE_PARENT, "number_children": 3},
        {"uuid": "8054fc2e-b635-4ae6-9553-7f4d0ee1071a", "lower": 45529, "upper": 101179, "family_type": models.FamilyType.SINGLE_PARENT, "number_children": 4},
    ]:
        cmg_a_r = db.query(models.CMGAmountRange).filter(models.CMGAmountRange.uuid == cmg_a_r_item["uuid"]).first()
        if not cmg_a_r:
            cmg_a_r = models.CMGAmountRange(
                uuid=cmg_a_r_item["uuid"],
                lower=cmg_a_r_item["lower"],
                upper=cmg_a_r_item["upper"],
                family_type=cmg_a_r_item["family_type"],
                number_children=cmg_a_r_item["number_children"]
            )
        else:
            cmg_a_r.lower = cmg_a_r_item["lower"]
            cmg_a_r.upper = cmg_a_r_item["upper"]
            cmg_a_r.family_type = cmg_a_r_item["family_type"]
            cmg_a_r.number_children = cmg_a_r_item["number_children"]
        db.add(cmg_a_r)
    db.commit()

    return {"message": "Default CMG amount range created successfully"}


@router.post("/create-cmg-amount", response_model=schemas.Msg, status_code=201)
async def create_user_roles(
        db: Session = Depends(dependencies.get_db),
        admin_key: schemas.AdminKey = Body(...)
) -> dict[str, str]:
    check_user_access_key(admin_key)

    for cmg_a_item in [
        {"uuid": "d6a7ece0-93c2-4898-9ce2-a5384449b518", "child_age_lower": 0, "child_age_upper": 3, "tranche_1_amount": 967.83, "tranche_2_amount": 834.30, "tranche_3_amount": 700.82},
        {"uuid": "eccb6591-3da3-404e-914d-1e63a088da82", "child_age_lower": 3, "child_age_upper": 6, "tranche_1_amount": 483.91, "tranche_2_amount": 417.15, "tranche_3_amount": 350.42}
    ]:
        cmg_a = db.query(models.CMGAmount).filter(models.CMGAmount.uuid == cmg_a_item["uuid"]).first()
        if not cmg_a:
            cmg_a = models.CMGAmount(
                uuid=cmg_a_item["uuid"],
                child_age_lower=cmg_a_item["child_age_lower"],
                child_age_upper=cmg_a_item["child_age_upper"],
                tranche_1_amount=cmg_a_item["tranche_1_amount"],
                tranche_2_amount=cmg_a_item["tranche_2_amount"],
                tranche_3_amount=cmg_a_item["tranche_3_amount"]
            )
        else:
            cmg_a.child_age_lower = cmg_a_item["child_age_lower"]
            cmg_a.child_age_upper = cmg_a_item["child_age_upper"]
            cmg_a.tranche_1_amount = cmg_a_item["tranche_1_amount"]
            cmg_a.tranche_2_amount = cmg_a_item["tranche_2_amount"]
            cmg_a.tranche_3_amount = cmg_a_item["tranche_3_amount"]
        db.add(cmg_a)
    db.commit()
    return {"message": "Default CMG amount created successfully"}


@router.put("/set-old-nurseries-code")
def set_code_old_nurseries(
    db: Session = Depends(dependencies.get_db),
    admin_key: schemas.AdminKey = Body(...)
):
    check_user_access_key(admin_key)
    for nursery in db.query(models.Nursery).all():
        code_from_name = "".join([word[0] for word in nursery.name.split(" ")])
        code = code_from_name
        while db.query(models.Nursery).filter(models.Nursery.code == code).first():
            if code == code_from_name:
                code = code + "1"
            else:
                if int(code[-1]) <= 9:
                    code = code_from_name + str(int(code[-1]) + 1)
                elif code[-2] == "99":
                    code = code_from_name + str(int(code[-2]) + 1)
                elif code[-3] == "999":
                    code = code_from_name + str(int(code[-4]) + 1)
        nursery.code = code
        db.commit()
    return {"message": "Old nurseries code created successfully"}


@router.put("/invoice-reference")
def set_old_invoices_reference(
    db: Session = Depends(dependencies.get_db),
    admin_key: schemas.AdminKey = Body(...)
):
    check_user_access_key(admin_key)
    for nursery in db.query(models.Nursery).all():
        invoices = db.query(models.Invoice).filter(models.Invoice.nursery_uuid == nursery.uuid).order_by(models.Invoice.date_added.desc()).all()

        ref_number = 1
        for invoice in invoices:
            invoice.reference = f"{ref_number}-{invoice.nursery.code}-{datetime.now().strftime('%m%y')}"
            invoice.id = ref_number
            db.commit()
            ref_number += 1
