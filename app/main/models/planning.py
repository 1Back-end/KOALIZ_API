from dataclasses import dataclass
from datetime import date, datetime
import enum
from sqlalchemy.sql import func
from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, String, Integer, DateTime, Table, Text, Time
from sqlalchemy import event
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.ext.hybrid import hybrid_property

from app.main.models.db.base_class import Base
from app.main.models.db.session import SessionLocal


@dataclass
class Year(Base):

    """ Year Model for storing years related details """

    __tablename__ = "years"

    uuid = Column(String, primary_key=True, unique=True)

    year: int = Column(Integer, nullable=False, default=2024)

    date_added: any = Column(DateTime, server_default=func.now())
    date_modified: any = Column(DateTime, server_default=func.now())


@dataclass
class Month(Base):

    """ Month Model for storing months related details """

    __tablename__ = "months"

    uuid = Column(String, primary_key=True, unique=True)
    start_date: date = Column(Date, nullable=False)
    end_date: date = Column(Date, nullable=False)

    year_uuid: str = Column(String, ForeignKey('years.uuid'), nullable=True)
    year = relationship("Year", foreign_keys=[year_uuid], uselist=False)

    date_added: any = Column(DateTime, server_default=func.now())
    date_modified: any = Column(DateTime, server_default=func.now())


@dataclass
class Week(Base):

    """ Week Model for storing weeks related details """

    __tablename__ = "weeks"

    uuid = Column(String, primary_key=True, unique=True)
    start_date: date = Column(Date, nullable=False)
    end_date: date = Column(Date, nullable=False)
    week_index: int = Column(Integer, nullable=False)

    month_uuid: str = Column(String, ForeignKey('months.uuid'), nullable=True)
    month = relationship("Month", foreign_keys=[month_uuid], uselist=False)

    date_added: any = Column(DateTime, server_default=func.now())
    date_modified: any = Column(DateTime, server_default=func.now())


@dataclass
class Day(Base):

    """ Day Model for storing days related details """

    __tablename__ = "days"

    uuid = Column(String, primary_key=True, unique=True)
    day: date = Column(Date, nullable=False)
    day_of_week: str = Column(String, nullable=False)

    month_uuid: str = Column(String, ForeignKey('months.uuid'), nullable=True)
    month = relationship("Month", foreign_keys=[month_uuid], uselist=False)

    year_uuid: str = Column(String, ForeignKey('years.uuid'), nullable=True)
    year = relationship("Year", foreign_keys=[year_uuid], uselist=False)

    week_uuid: str = Column(String, ForeignKey('weeks.uuid'), nullable=True)
    week = relationship("Week", foreign_keys=[week_uuid], uselist=False)

    date_added: any = Column(DateTime, server_default=func.now())
    date_modified: any = Column(DateTime, server_default=func.now())


# class MealQuality(enum.Enum):
#     Pas = "Pas"
#     Peu = "Peu"
#     Bien = "Bien"
#     Très = "Très"

# Repas
@dataclass
class Meal(Base):

    """ Meal Model for storing meals related details """

    __tablename__ = "meals"

    uuid = Column(String, primary_key=True, unique=True)

    meal_time = Column(DateTime, nullable=False, default=datetime.now()) # Heure
    bottle_milk_ml = Column(Integer, nullable=True) # Biberon
    breastfeeding_duration_minutes = Column(Integer, nullable=True) # Allaitement
    meal_quality = Column(String, nullable=False) # Comment l’enfant a manger (Pas, Peu, Bien, Très)
    observation = Column(Text, nullable=True) # Observation

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=False)
    child: Mapped[any] = relationship("Child", foreign_keys=child_uuid, uselist=False, back_populates="meals")

    # added_by_uuid: str = Column(String, ForeignKey('owners.uuid'), nullable=True) TODO change this with kind model link
    # added_by = relationship("Owner", foreign_keys=[added_by_uuid], uselist=False)

    date_added: any = Column(DateTime, server_default=func.now())
    date_modified: any = Column(DateTime, server_default=func.now())

@dataclass
class Activity(Base):

    """ Activity model representing activities """

    __tablename__ = "activities"
    
    uuid = Column(String, primary_key=True, unique=True)
    activity_name = Column(String, nullable=False)
    activity_time = Column(DateTime, nullable=False, default=datetime.now())
    # added_by_uuid: str = Column(String, ForeignKey('owners.uuid'), nullable=True) TODO change this with kind model link
    # added_by = relationship("Owner", foreign_keys=[added_by_uuid], uselist=False)
    
    date_added = Column(DateTime, server_default=func.now())
    date_modified = Column(DateTime, server_default=func.now())

    children = relationship("ChildActivity", back_populates="activity")

@dataclass
class ChildActivity(Base):

    """ ChildActivity model representing the many-to-many relationship between children and activities """

    __tablename__ = "child_activities"
    
    child_uuid = Column(String, ForeignKey('children.uuid'), primary_key=True)
    activity_uuid = Column(String, ForeignKey('activities.uuid'), primary_key=True)
    
    child = relationship("Child", back_populates="activities")
    activity = relationship("Activity", back_populates="children")

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

# class NapQuality(enum.Enum):
#     Repos_seulement = "Repos seulement"
#     Peu_dormi = "Peu dormi"
#     Bien_dormi = "Bien dormi"
#     Très_bien_dormi = "Très bien dormi"

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
    quality = Column(String, nullable=False) #  Qualité (Repos seulement, peu dormi, bien dormi, très bien dormi)
    observation = Column(Text, nullable=True)

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    # added_by_uuid: str = Column(String, ForeignKey('owners.uuid'), nullable=True) TODO change this with kind model link
    # added_by = relationship("Owner", foreign_keys=[added_by_uuid], uselist=False)
    
    date_added = Column(DateTime, server_default=func.now())
    date_modified = Column(DateTime, server_default=func.now())

    @hybrid_property
    def duration(self):
        db = SessionLocal()
        if self.end_time:
            duration = (self.end_time - self.start_time).total_seconds() / 3600  # en heures
            return duration
        return 0


# class CareType(enum.Enum):
#     Poids = "Poids"
#     Température = "Température"
#     Médicament = "Médicament"

# class Route(enum.Enum):
#     Axilliaire = "Axilliaire"
#     Orale = "Orale"
#     Front = "Front"
#     Rectale = "Rectale"
#     Tempe = "Tempe"

# class MedicationType(enum.Enum):
#     Suppositoire = "Suppositoire"
#     Sirop = "Sirop"
#     Comprimé = "Comprimé"
#     Autre = "Autre"


@dataclass
class HealthRecord(Base):

    """ HealthRecord model representing health records of children """

    __tablename__ = "health_records"

    uuid = Column(String, primary_key=True, unique=True)

    child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=False)
    child: Mapped[any] = relationship("Child", foreign_keys=child_uuid, uselist=False, back_populates="health_records")

    care_type = Column(String, nullable=False) # Types de soins (poids, température, médicament)
    time = Column(DateTime, nullable=False, default=datetime.now())
    weight = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    route = Column(String, nullable=True) # voie (Axilliaire, Orale, Front, Rectale, Tempe)
    medication_type = Column(String, nullable=True) # Type (suppositoire, Sirop, Comprimé, Autre)
    medication_name = Column(String, nullable=True)
    observation = Column(Text, nullable=True)

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)

    # added_by_uuid: str = Column(String, ForeignKey('owners.uuid'), nullable=True) TODO change this with kind model link
    # added_by = relationship("Owner", foreign_keys=[added_by_uuid], uselist=False)

    date_added = Column(DateTime, server_default=func.now())
    date_modified = Column(DateTime, server_default=func.now())


# class Cleanliness(enum.Enum):
#     Rien_a_signaler = "Rien a signaler"
#     Couche = "Couche"
#     Sur_le_pot = "Sur le pot"
#     Aux_toilettes = "Aux toilettes"

# class StoolType(enum.Enum):
#     Dures = "Dures"
#     Normales = "Normales"
#     Molles = "Molles"
#     Liquides = "Liquides"

# class AdditionalCare(enum.Enum):
#     Nez = "Nez"
#     Yeux = "Yeux"
#     Oreilles = "Oreilles"
#     Crème = "Crème"


@dataclass
class HygieneChange(Base):

    """ HygieneChange model representing hygiene changes of children """

    __tablename__ = "hygiene_changes"
    
    uuid = Column(String, primary_key=True, unique=True)

    child_uuid: str = Column(String, ForeignKey('children.uuid'), nullable=False)
    child: Mapped[any] = relationship("Child", foreign_keys=child_uuid, uselist=False, back_populates="hygiene_changes")

    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid'), nullable=True)
    nursery: Mapped[any] = relationship("Nursery", foreign_keys=nursery_uuid, uselist=False)
    
    time = Column(DateTime, nullable=False, default=datetime.now())
    cleanliness = Column(String, nullable=False) # Propreté (Rien a signaler, Couche, Sur le pot, Aux toilettes)
    pipi = Column(Boolean, nullable=False, default=False)
    stool_type = Column(String, nullable=True) # (Dures, normales, molles, liquides)
    additional_care = Column(String, nullable=True) # Soins complémentaires (Nez, yeux, Oreilles, Crème
    observation = Column(Text, nullable=True)

    # added_by_uuid: str = Column(String, ForeignKey('owners.uuid'), nullable=True) TODO change this with kind model link
    # added_by = relationship("Owner", foreign_keys=[added_by_uuid], uselist=False)
    
    date_added = Column(DateTime, server_default=func.now())
    date_modified = Column(DateTime, server_default=func.now())


# class MediaType(enum.Enum):
#     Photo = "Photo"
#     Video = "Video"

children_media = Table('children_media', Base.metadata,
    Column('child_uuid', String, ForeignKey('children.uuid')),
    Column('media_uuid', String, ForeignKey('media.uuid'))
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
    
    media_type = Column(String, nullable=False) # media type (photos, vidéo)
    time = Column(DateTime, nullable=False, default=datetime.now())
    observation = Column(Text, nullable=True)

    # added_by_uuid: str = Column(String, ForeignKey('owners.uuid'), nullable=True) TODO change this with kind model link
    # added_by = relationship("Owner", foreign_keys=[added_by_uuid], uselist=False)
    
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

    # added_by_uuid: str = Column(String, ForeignKey('owners.uuid'), nullable=True) TODO change this with kind model link
    # added_by = relationship("Owner", foreign_keys=[added_by_uuid], uselist=False)
    
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
