from dataclasses import dataclass
from enum import Enum
from datetime import date, datetime
from sqlalchemy.sql import func
from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, String, Integer, DateTime, Table, Text, Time, types
from sqlalchemy import event
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.ext.hybrid import hybrid_property

from app.main.models.db.base_class import Base
from app.main.models.db.session import SessionLocal


class MealQuality(str, Enum):
    NONE = "NONE" # Pas
    LITTLE = "LITTLE" # Peu
    GOOD = "GOOD" # Bien
    VERY_GOOD = "VERY_GOOD" # Très

class MealTypeEnum(str, Enum):
    BOTTLE_FEEDING = "BOTTLE_FEEDING" #Le biberon
    BREAST_FEEDING = "BREAST_FEEDING" #l'allaitement

# Repas
@dataclass
class Meal(Base):

    """ Meal Model for storing meals related details """

    __tablename__ = "meals"

    uuid = Column(String, primary_key=True, unique=True)

    meal_time = Column(DateTime, nullable=False, default=datetime.now()) # Heure
    bottle_milk_ml = Column(Integer, nullable=True) # Biberon
    # breastfeeding_duration_minutes = Column(Integer, nullable=True) # Allaitement
    meal_quality = Column(types.Enum(MealQuality), nullable=False) # Comment l’enfant a manger (Pas, Peu, Bien, Très)
    meal_type = Column(String, nullable=True,) # Comment l’enfant a manger (Pas, Peu, Bien, Très)
    observation = Column(Text, nullable=True) # Observation

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=False)
    child: Mapped[any] = relationship("Child", foreign_keys=child_uuid, uselist=False, back_populates="meals")

    added_by_uuid: str = Column(String, ForeignKey('employees.uuid'), nullable=True)
    added_by = relationship("Employee", foreign_keys=[added_by_uuid], uselist=False)

    date_added: any = Column(DateTime, server_default=func.now())
    date_modified: any = Column(DateTime, server_default=func.now())


# Table d'association many-to-many entre Activity et Category
activity_category_table = Table('activity_category', Base.metadata,
    Column('activity_uuid', String, ForeignKey('activities.uuid'), primary_key=True),
    Column('category_uuid', String, ForeignKey('activity_categories.uuid'), primary_key=True)
)

@dataclass
class ActivityCategory(Base):

    """ ActivityCategory model representing activities categories """

    __tablename__ = "activity_categories"
    
    uuid = Column(String, primary_key=True, unique=True)
    name_fr = Column(String, nullable=False)
    name_en = Column(String, nullable=False)

    activities = relationship("Activity", secondary=activity_category_table, back_populates="activity_categories")

    date_added = Column(DateTime, server_default=func.now())
    date_modified = Column(DateTime, server_default=func.now())

@dataclass
class Activity(Base):

    """ Activity model representing activities """

    __tablename__ = "activities"

    uuid = Column(String, primary_key=True, unique=True)
    name_fr = Column(String, nullable=False)
    name_en = Column(String, nullable=False)

    children = relationship("ChildActivity", back_populates="activity")
    activity_categories = relationship("ActivityCategory", secondary=activity_category_table, back_populates="activities")

    date_added = Column(DateTime, server_default=func.now())
    date_modified = Column(DateTime, server_default=func.now())


@dataclass
class ChildActivity(Base):

    """ ChildActivity model representing the many-to-many relationship between children and activities """

    __tablename__ = "children_activities"

    child_uuid = Column(String, ForeignKey('children.uuid'), primary_key=True)
    child = relationship("Child", back_populates="activities")

    activity_uuid = Column(String, ForeignKey('activities.uuid'), primary_key=True)
    activity = relationship("Activity", back_populates="children")

    added_by_uuid: str = Column(String, ForeignKey('employees.uuid'), nullable=True)
    added_by = relationship("Employee", foreign_keys=[added_by_uuid], uselist=False)

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    activity_time = Column(DateTime, nullable=False, default=datetime.now())

    date_added = Column(DateTime, server_default=func.now())
    date_modified = Column(DateTime, server_default=func.now())


class NapQuality(str, Enum):
    REST_ONLY = "REST_ONLY" # Repos seulement
    LITTLE_SLEEP = "LITTLE_SLEEP" # Peu dormi
    WELL_SLEEP = "WELL_SLEEP" # Bien dormi
    VERY_WELL_SLEEP = "VERY_WELL_SLEEP" # Très bien dormi

# Sieste
@dataclass
class Nap(Base):

    """ Nap model representing naps taken by children """

    __tablename__ = "naps"
    
    uuid = Column(String, primary_key=True, unique=True)

    child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=False)
    child: Mapped[any] = relationship("Child", foreign_keys=child_uuid, uselist=False, back_populates="naps")
    
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    quality = Column(types.Enum(NapQuality), nullable=False) #  Qualité (Repos seulement, peu dormi, bien dormi, très bien dormi)
    observation = Column(Text, nullable=True)

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    added_by_uuid: str = Column(String, ForeignKey('employees.uuid'), nullable=True)
    added_by = relationship("Employee", foreign_keys=[added_by_uuid], uselist=False)
    
    date_added = Column(DateTime, server_default=func.now())
    date_modified = Column(DateTime, server_default=func.now())

    @hybrid_property
    def duration(self):
        db = SessionLocal()
        if self.end_time:
            duration = (self.end_time - self.start_time).total_seconds() / 3600  # en heures
            return int(duration)
        return 0


class CareType(str, Enum):
    WEIGHT = "WEIGHT" # Poids
    TEMPERATURE = "TEMPERATURE" # Température
    MEDICATION = "MEDICATION" # Médicament

class Route(str, Enum):
    AXILLARY = "AXILLARY" # Axilliaire
    ORAL = "ORAL" # Orale
    FOREHEAD = "FOREHEAD" # Front
    RECTAL = "RECTAL" # Rectale
    TEMPLE = "TEMPLE" # Tempe

class MedicationType(str, Enum):
    SUPPOSITORY = "SUPPOSITORY" # Suppositoire
    SYRUP = "SYRUP" # Sirop
    TABLET = "TABLET" # Comprimé
    OTHER = "OTHER" # Autre

@dataclass
class HealthRecord(Base):

    """ HealthRecord model representing health records of children """

    __tablename__ = "health_records"

    uuid = Column(String, primary_key=True, unique=True)

    child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=False)
    child: Mapped[any] = relationship("Child", foreign_keys=child_uuid, uselist=False, back_populates="health_records")

    care_type = Column(types.Enum(CareType), nullable=False) # Types de soins (poids, température, médicament)
    time = Column(DateTime, nullable=False, default=datetime.now())
    weight = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    route = Column(types.Enum(Route), nullable=True) # voie (Axilliaire, Orale, Front, Rectale, Tempe)
    medication_type = Column(types.Enum(MedicationType), nullable=True) # Type (suppositoire, Sirop, Comprimé, Autre)
    medication_name = Column(String, nullable=True)
    observation = Column(Text, nullable=True)

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    added_by_uuid: str = Column(String, ForeignKey('employees.uuid'), nullable=True)
    added_by = relationship("Employee", foreign_keys=[added_by_uuid], uselist=False)

    date_added = Column(DateTime, server_default=func.now())
    date_modified = Column(DateTime, server_default=func.now())


class Cleanliness(str, Enum):
    NOTHING_TO_REPORT = "NOTHING_TO_REPORT" # Rien a signaler
    DIAPER = "DIAPER" # Couche
    POTTY = "POTTY" # Sur le pot
    TOILET = "TOILET" # Aux toilettes

class StoolType(str, Enum):
    HARD = "HARD" # Dures
    NORMAL = "NORMAL" # Normales
    SOFT = "SOFT" # Molles
    LIQUID = "LIQUID" # Liquides

class AdditionalCare(str, Enum):
    NOSE = "NOSE" # Nez
    EYES = "EYES" # Yeux
    EARS = "EARS" # Oreilles
    CREAM = "CREAM" # Crème


@dataclass
class HygieneChange(Base):

    """ HygieneChange model representing hygiene changes of children """

    __tablename__ = "hygiene_changes"
    
    uuid = Column(String, primary_key=True, unique=True)

    child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=False)
    child: Mapped[any] = relationship("Child", foreign_keys=child_uuid, uselist=False, back_populates="hygiene_changes")

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=False)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)
    
    time = Column(DateTime, nullable=False, default=datetime.now())
    cleanliness = Column(types.Enum(Cleanliness), nullable=False) # Propreté (Rien a signaler, Couche, Sur le pot, Aux toilettes)
    pipi = Column(Boolean, nullable=False, default=False)
    stool_type = Column(types.Enum(StoolType), nullable=True) # (Dures, normales, molles, liquides)
    additional_care = Column(types.Enum(AdditionalCare), nullable=True) # Soins complémentaires (Nez, yeux, Oreilles, Crème)
    observation = Column(Text, nullable=True)

    added_by_uuid: str = Column(String, ForeignKey('employees.uuid'), nullable=False)
    added_by = relationship("Employee", foreign_keys=[added_by_uuid], uselist=False)
    
    date_added = Column(DateTime, server_default=func.now())
    date_modified = Column(DateTime, server_default=func.now())


class MediaType(str, Enum):
    PHOTO = "PHOTO"
    VIDEO = "VIDEO"

children_media = Table('children_media', Base.metadata,
    Column('child_uuid', String, ForeignKey('children.uuid',ondelete='CASCADE',onupdate='CASCADE')),
    Column('media_uuid', String, ForeignKey('media.uuid',ondelete='CASCADE',onupdate='CASCADE'))
)

@dataclass
class Media(Base):

    """ Media model representing media (photos, videos) """

    __tablename__ = "media"
    
    uuid = Column(String, primary_key=True, unique=True)

    file_uuid: str = Column(String, ForeignKey('storages.uuid'), nullable=True)
    file = relationship("Storage", foreign_keys=[file_uuid])    

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)
    
    media_type = Column(types.Enum(MediaType), nullable=False) # media type (photos, vidéo)
    time = Column(DateTime, nullable=False, default=datetime.now())
    observation = Column(Text, nullable=True)

    added_by_uuid: str = Column(String, ForeignKey('employees.uuid'), nullable=True)
    added_by = relationship("Employee", foreign_keys=[added_by_uuid], uselist=False)
    
    date_added = Column(DateTime, server_default=func.now())
    date_modified = Column(DateTime, server_default=func.now())
    
    children = relationship("Child", secondary=children_media, back_populates="media")


@dataclass
class Observation(Base):

    """ Observation model representing observations of children """

    __tablename__ = "observations"

    uuid = Column(String, primary_key=True, unique=True)

    child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=False)
    child: Mapped[any] = relationship("Child", foreign_keys=child_uuid, uselist=False, back_populates="observations")

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    time = Column(DateTime, nullable=False, default=datetime.now())
    observation = Column(Text, nullable=False)

    added_by_uuid: str = Column(String, ForeignKey('employees.uuid'), nullable=True)
    added_by = relationship("Employee", foreign_keys=[added_by_uuid], uselist=False)

    date_added = Column(DateTime, server_default=func.now())
    date_modified = Column(DateTime, server_default=func.now())


''' Attendance Table : Gère les horaires d'arrivée et de départ. '''
@dataclass
class Attendance(Base):

    """ Attendance model representing attendances of children """

    __tablename__ = "attendances"

    uuid = Column(String, primary_key=True, unique=True)

    child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=False)
    child: Mapped[any] = relationship("Child", foreign_keys=child_uuid, uselist=False, back_populates="attendances")

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    date = Column(Date, nullable=False)
    arrival_time = Column(DateTime, nullable=True)
    departure_time = Column(DateTime, nullable=True)

    added_by_uuid: str = Column(String, ForeignKey('employees.uuid'), nullable=True)
    added_by = relationship("Employee", foreign_keys=[added_by_uuid], uselist=False)

    date_added = Column(DateTime, server_default=func.now())
    date_modified = Column(DateTime, server_default=func.now())


''' Absences Table : Permet de noter les absences avec une plage de temps et une note. '''
@dataclass
class Absence(Base):

    """ Absence model representing absences of children """

    __tablename__ = "absences"

    uuid = Column(String, primary_key=True, unique=True)

    child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=False)
    child: Mapped[any] = relationship("Child", foreign_keys=child_uuid, uselist=False)

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    note = Column(Text, nullable=True)

    added_by_uuid: str = Column(String, ForeignKey('employees.uuid'), nullable=True)
    added_by = relationship("Employee", foreign_keys=[added_by_uuid], uselist=False)

    date_added = Column(DateTime, server_default=func.now())
    date_modified = Column(DateTime, server_default=func.now())


""" OccasionalPresence Table : Permet d'enregistrer les présences occasionnelles avec des détails spécifiques."""
@dataclass
class OccasionalPresence(Base):

    """ OccasionalPresence model representing occasional presence of children """

    __tablename__ = "occasional_presences"

    uuid = Column(String, primary_key=True, unique=True)

    child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=False)
    child: Mapped[any] = relationship("Child", foreign_keys=child_uuid, uselist=False)

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    note = Column(Text, nullable=True)

    added_by_uuid: str = Column(String, ForeignKey('employees.uuid'), nullable=True)
    added_by = relationship("Employee", foreign_keys=[added_by_uuid], uselist=False)

    date_added = Column(DateTime, server_default=func.now())
    date_modified = Column(DateTime, server_default=func.now())


# SQLAlchemy event listeners for automatic timestamps
@event.listens_for(Base, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the create/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()

@event.listens_for(Base, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()
