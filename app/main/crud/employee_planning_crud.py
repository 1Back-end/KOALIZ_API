import math
from typing import Optional
import uuid
from datetime import timedelta
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.main.crud.base import CRUDBase
from app.main.models import EmployeePlanning, Day, Nursery,Employee
from app.main.schemas import EmployeePlanningCreate, EmployeePlanningUpdate,EmployeePlanningList



class CRUDEmployeePlanning(CRUDBase[EmployeePlanning, EmployeePlanningCreate, EmployeePlanningUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, planning_uuid: str):
        return db.query(EmployeePlanning).filter(EmployeePlanning.uuid == planning_uuid).first()

    
    @classmethod
    def insert_planning_for_employee(cls, nursery: Nursery, employee: Employee, db: Session):
        start = employee.begin_date
        end = employee.end_date
        planning_list =[]

        print(f"Inserting:{start}-{end}")
        print(f"nursery:{nursery}-{employee}")

        # Itérer sur chaque jour entre le début et la fin du contrat
        date_range = [start + timedelta(days=delta) for delta in range((end - start).days + 1)]
        num_weeks = len(employee.typical_weeks)  # Nombre de semaines typiques

        print("date_range",date_range)
        print("num_weeks",num_weeks)
        for current_date in date_range:
            weekday = current_date.weekday()  # Obtenir le jour de la semaine (lundi=0, dimanche=6)
            print("1current_date1",current_date)

            print("weekday",weekday)
            # Déterminer quelle semaine typique utiliser
            tw_index = (current_date - start).days // 7 % num_weeks
            typical_week = employee.typical_weeks[tw_index]

            print("typical_week",typical_week)
            print("tw_index",tw_index)
            # Vérifier si c'est un jour ouvrable (lundi=0 à vendredi=4)
            if weekday < len(typical_week) and len(typical_week[weekday]) > 0:
                print("if-weekday",weekday)
                print("len(typical_week)",len(typical_week[weekday]))

                # Rechercher le jour dans la base de données
                day = db.query(Day).filter(Day.day == current_date).first()
                print("day",day)
                if day:
                    print("if-day",day)
                    # Vérifier si une entrée pour cette combinaison nursery, child et day existe déjà
                    existing_planning = db.query(EmployeePlanning).filter_by(
                        nursery_uuid=nursery.uuid,
                        employee_uuid=employee.uuid,
                        day_uuid=day.uuid
                    ).first()

                    if not existing_planning:
                        # Si l'entrée n'existe pas, la créer
                        planning = EmployeePlanning(
                            uuid=str(uuid.uuid4()),  # Générer un UUID unique
                            nursery_uuid=nursery.uuid,
                            employee_uuid=employee.uuid,
                            day_uuid=day.uuid,
                            current_date=current_date
                        )
                        db.add(planning)

                        planning_list.append(planning)
                        db.commit()  # Commit une fois après la boucle

        print(planning_list)
        return planning_list
    
    @classmethod
    def get_multi(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 30,
        employee_uuid:Optional[str] = None,
        nursery_uuid: Optional[str] = None,
        order: Optional[str] = None
        # order_filed:Optional[str] = None   
    ):
        record_query = db.query(EmployeePlanning)
        
           

       
        if nursery_uuid:
            record_query = record_query.filter(EmployeePlanning.nursery_uuid == nursery_uuid)
        
        if order and order.lower() == "asc":
            record_query = record_query.order_by(EmployeePlanning.date_added.asc())
        
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(EmployeePlanning.date_added.desc())

        if employee_uuid:
            record_query = record_query.filter(EmployeePlanning.employee_uuid == employee_uuid)

        total = record_query.count()
        
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return EmployeePlanningList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )
    

employee_planning = CRUDEmployeePlanning(EmployeePlanning)
