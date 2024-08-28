from dataclasses import dataclass
from .user import UserStatusType
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, Table, Boolean,types,event
from datetime import datetime, date
from sqlalchemy.orm import relationship
from .db.base_class import Base
from enum import Enum

class EmployeStatusEnum(str,Enum):
    ACTIVED = "ACTIVED" # L'employé est actuellement actif et en service.
    UNACTIVED = "UNACTIVED" # L'employé est inactif, peut-être en congé ou en pause.
    DELETED = "DELETED" # L'employé a quitté l'entreprise de manière permanente.
    SUSPENDED = "SUSPENDED"# L'employé est temporairement suspendu pour des raisons disciplinaires.
    RETIRED = "RETIRED" # L'employé a pris sa retraite.
    PROBATION = "PROBATION" #L'employé est en période d'essai.

class TeamStatusEnum(str,Enum):
    ACTIVED = "ACTIVED" # L'employé est actuellement actif et en service.
    UNACTIVED = "UNACTIVED" # L'employé est inactif, peut-être en congé ou en pause.
    DELETED = "DELETED" # L'employé a quitté l'entreprise de manière permanente.


@dataclass
class Team(Base):
    """ Database class for storing team information"""
    __tablename__ = 'teams'
    uuid: str = Column(String, primary_key=True, unique=True, index=True)
    name:str = Column(String, index=True,nullable = False)
    description: str = Column(Text)

    # owner_uuid: str = Column(String, ForeignKey('owners.uuid',ondelete="CASCADE",onupdate="CASCADE"), nullable=False)
    # owner = relationship("Owner", foreign_keys=[owner_uuid], uselist=False)

    leader_uuid: str = Column(String, ForeignKey('employees.uuid',ondelete="CASCADE",onupdate="CASCADE"), nullable=False)
    leader = relationship("Employee", foreign_keys=[leader_uuid], uselist=False)
    
    status:str = Column(String, index=True, nullable=False)
    employees = relationship("Employee", secondary="team_employees", back_populates="teams",overlaps="employee,team")

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<Team: uuid: {} name: {} leader: {}>'.format(self.uuid, self.name,self.leader)


@event.listens_for(Team, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(Team, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()
    
@dataclass
class Employee(Base):
    """ Database class for storing employee information"""
    __tablename__ = 'employees'
    uuid: str = Column(String, primary_key=True, unique=True, index=True)
    email: str = Column(String, nullable=False, default="", index=True)
    firstname: str = Column(String(100), nullable=False, default="")

    lastname: str = Column(String(100), nullable=False, default="")    
    avatar_uuid: str = Column(String, ForeignKey('storages.uuid'), nullable=True)
    avatar = relationship("Storage", foreign_keys=[avatar_uuid], uselist=False)

    teams = relationship("Team",secondary="team_employees", back_populates="employees",overlaps="team,employee")

    nurseries = relationship("Nursery", secondary="nursery_employees", back_populates="employees",overlaps="employee,nursery")
    # nurseries = relationship("Nursery", secondary="nursery_memberships", back_populates="memberships",overlaps="memberships, nursery")

    status:str = Column(String, index=True, nullable=False)
    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())
    
    def __repr__(self):
        return '<Employee: uuid: {} email: {} firstname: {} lastname: {}>'.format(self.uuid,self.email, self.firstname, self.lastname)
    
@event.listens_for(Employee, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(Employee, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()    


@dataclass
class NurseryEmployees(Base):
    __tablename__ = 'nursery_employees'
    uuid: str = Column(String, primary_key=True, unique=True, index=True)
    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid',ondelete="CASCADE",onupdate="CASCADE"), nullable=False)
    nursery = relationship("Nursery", foreign_keys=[nursery_uuid], uselist=False, overlaps="employees")

    employee_uuid: str = Column(String, ForeignKey('employees.uuid',ondelete="CASCADE",onupdate="CASCADE"), nullable=False)
    employee = relationship("Employee", foreign_keys=[employee_uuid], uselist=False, overlaps="nurseries")

    status:str = Column(String, index=True, nullable=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

@event.listens_for(NurseryEmployees, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(NurseryEmployees, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()   

@dataclass
class TeamEmployees(Base):
    __tablename__ = 'team_employees'
    uuid: str = Column(String, primary_key=True, unique=True, index=True)
    employee_uuid: str = Column(String, ForeignKey('employees.uuid',ondelete="CASCADE",onupdate="CASCADE"), nullable=False)
    employee = relationship("Employee", foreign_keys=[employee_uuid], uselist=False, overlaps="teams")

    team_uuid: str = Column(String, ForeignKey('teams.uuid',ondelete="CASCADE",onupdate="CASCADE"), nullable=False)
    team = relationship("Team", foreign_keys=[team_uuid], uselist=False,overlaps="employees")

    status:str = Column(String, index=True, nullable=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<TeamEmployee: uuid: {} employee_uuid: {} team_uuid: {}>'.format(self.uuid, self.employee_uuid, self.team_uuid)

@dataclass
class Group(Base):
    __tablename__ = 'groups'
    uuid: str = Column(String, primary_key=True, unique=True, index=True)
    title_en: str = Column(String, nullable=False)
    title_fr: str = Column(String, nullable=False)

    code: str = Column(String, nullable=False,unique=True)
    description: str = Column(String, nullable=True)

    def __repr__(self):
        return '<Group: uuid: {} title_fr: {} title_en: {}>'.format(self.uuid, self.title_fr, self.title_en)


@dataclass
class EmployeeRoles(Base):
    __tablename__ = 'employee_roles'
    uuid: str = Column(String, primary_key=True, unique=True, index=True)
    employee_uuid: str = Column(String, ForeignKey('employees.uuid',ondelete="CASCADE",onupdate="CASCADE"), nullable=False)
    employee = relationship("Employee", foreign_keys=[employee_uuid], uselist=False, overlaps="teams")

    team_uuid: str = Column(String, ForeignKey('teams.uuid',ondelete="CASCADE",onupdate="CASCADE"), nullable=False)
    team = relationship("Team", foreign_keys=[team_uuid], uselist=False,overlaps="employees")

    status:str = Column(String, index=True, nullable=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<TeamEmployee: uuid: {} employee_uuid: {} team_uuid: {}>'.format(self.uuid, self.employee_uuid, self.team_uuid)

@event.listens_for(TeamEmployees, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(TeamEmployees, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()   
