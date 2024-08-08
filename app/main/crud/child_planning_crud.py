import uuid
from datetime import timedelta
from sqlalchemy.orm import Session
from app.main.crud.base import CRUDBase
from app.main.models import ChildPlanning, Day, Nursery, Child
from app.main.schemas import ChildPlanningCreate, ChildPlanningUpdate


class CRUDChildPlanning(CRUDBase[ChildPlanning, ChildPlanningCreate, ChildPlanningUpdate]):


    @classmethod
    def insert_planning(self, *, nursery: Nursery, child: Child, db: Session):
        start = child.contract.begin_date
        end = child.contract.end_date

        # Itérer sur chaque jour entre le début et la fin du contrat
        date_range = [start + timedelta(days=delta) for delta in range((end - start).days + 1)]
        num_weeks = len(child.contract.typical_weeks)  # Nombre de semaines typiques

        for current_date in date_range:
            weekday = current_date.weekday()  # Obtenir le jour de la semaine (lundi=0, dimanche=6)

            # Déterminer quelle semaine typique utiliser
            tw_index = (current_date - start).days // 7 % num_weeks
            typical_week = child.contract.typical_weeks[tw_index]

            # Vérifier si c'est un jour ouvrable (lundi=0 à vendredi=4)
            if weekday < len(typical_week) and len(typical_week[weekday]) > 0:
                # Rechercher le jour dans la base de données
                day = db.query(Day).filter(Day.day == current_date).first()

                if day:
                    # Vérifier si une entrée pour cette combinaison nursery, child et day existe déjà
                    existing_planning = db.query(ChildPlanning).filter_by(
                        nursery_uuid=nursery.uuid,
                        child_uuid=child.uuid,
                        day_uuid=day.uuid
                    ).first()

                    if not existing_planning:
                        # Si l'entrée n'existe pas, la créer
                        planning = ChildPlanning(
                            uuid=str(uuid.uuid4()),  # Générer un UUID unique
                            nursery_uuid=nursery.uuid,
                            child_uuid=child.uuid,
                            day_uuid=day.uuid,
                            current_date=current_date
                        )
                        db.add(planning)

        db.commit()  # Commit une fois après la boucle

child_planning = CRUDChildPlanning(ChildPlanning)
