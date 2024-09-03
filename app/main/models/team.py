from dataclasses import dataclass
from .user import UserStatusType
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, Table, Boolean,types,event
from sqlalchemy.ext.hybrid import hybrid_property
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
    groups = relationship("GroupTeams", back_populates="team")

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
    jobs = relationship("JobEmployees", back_populates="employee")

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

@event.listens_for(TeamEmployees, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()

@event.listens_for(TeamEmployees, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()

@dataclass
class Group(Base):
    __tablename__ = 'groups'
    uuid: str = Column(String, primary_key=True, unique=True, index=True)
    title_en: str = Column(String, nullable=False)
    title_fr: str = Column(String, nullable=False)

    code: str = Column(String, nullable=False)
    description: str = Column(String, nullable=True)
    teams = relationship("GroupTeams", back_populates="group")
    status:str = Column(String, index=True, nullable=False,default="CREATED")
    
    added_by_uuid: str = Column(String, ForeignKey('owners.uuid',ondelete = "CASCADE",onupdate= "CASCADE"), nullable=True)
    added_by = relationship("Owner", foreign_keys=[added_by_uuid], uselist=False)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<Group: uuid: {} title_fr: {} title_en: {} code: {}>'.format(self.uuid, self.title_fr, self.title_en,self.code)

    @hybrid_property
    def group_teams(self):
        response = []
        if self.teams:
            print("len122",len(self.teams))
            for group in self.teams:
                print("group",group)
                print("group.team",group.team)
                if  group.group_uuid == self.uuid and group.team.status!="DELETED":
                    print("deleted",group.team.status)
                    response.append(group.team)

        return response
        
@event.listens_for(Group, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()

@event.listens_for(Group, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()

@dataclass
class Job(Base):
    __tablename__ = 'jobs'
    uuid: str = Column(String, primary_key=True, unique=True, index=True)
    title_fr: str = Column(String, nullable=False)
    title_en: str = Column(String, nullable=False)

    description: str = Column(String, nullable=True)
    code: str = Column(String, nullable=True)
    status:str = Column(String, index=True, nullable=False,default="CREATED")

    employees = relationship("JobEmployees", back_populates="job")
    nurseries = relationship("NurseryJobs", back_populates="job")
    added_by_uuid: str = Column(String, ForeignKey('owners.uuid',ondelete = "CASCADE",onupdate= "CASCADE"), nullable=True)

    added_by = relationship("Owner", foreign_keys=[added_by_uuid], uselist=False)
    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<Job: uuid: {} title_fr: {} title_en: {} code: {} status: {}>'.format(self.uuid, self.title_fr, self.title_en,self.code,self.status)

    @hybrid_property
    def nursery_list(self):
        response = []
        if self.nurseries:
            print("len122",len(self.nurseries))
            for nusery_job in self.nurseries:
                print("nusery_job",nusery_job)
                print("nusery_job.nursey",nusery_job.nursery)
                if  nusery_job.job_uuid == self.uuid and nusery_job.nursery.status!="DELETED":
                    print("deleted",nusery_job.nursery.status)
                    response.append(nusery_job.nursery)

        return response
    
    @hybrid_property
    def employee_list(self):
        response = []
        if self.employees:
            print("len122",len(self.employees))
            for employee_job in self.employees:
                print("nusery_job",employee_job)
                print("nusery_job.nursey",employee_job.employee)
                if  employee_job.job_uuid == self.uuid and employee_job.employee.status!="DELETED":
                    print("deleted",employee_job.employee.status)
                    response.append(employee_job.employee)

        return response
    
@event.listens_for(Job, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()

@event.listens_for(Job, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()

@dataclass
class JobEmployees(Base):
    __tablename__ = 'job_employees'
    uuid: str = Column(String, primary_key=True, unique=True, index=True)
    employee_uuid: str = Column(String, ForeignKey('employees.uuid',ondelete="CASCADE",onupdate="CASCADE"), nullable=False)
    employee = relationship("Employee", foreign_keys=[employee_uuid], uselist=False)
    
    job_uuid: str = Column(String, ForeignKey('jobs.uuid',ondelete="CASCADE",onupdate="CASCADE"), nullable=False)
    job = relationship("Job", foreign_keys=[job_uuid], uselist=False)

    status:str = Column(String, index=True, nullable=False,default="CREATED")
    
    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<JobEmployees: uuid: {} employee_uuid: {} job_uuid: {} status: {}>'.format(self.uuid, self.employee_uuid, self.job_uuid,self.status)

@event.listens_for(JobEmployees, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()

@event.listens_for(JobEmployees, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()

@dataclass
class NurseryJobs(Base):
    __tablename__ = 'nursery_jobs'
    uuid: str = Column(String, primary_key=True, unique=True, index=True)
    nursery_uuid: str = Column(String, ForeignKey('nurseries.uuid',ondelete="CASCADE",onupdate="CASCADE"), nullable=False)
    nursery = relationship("Nursery", foreign_keys=[nursery_uuid], uselist=False)
    
    job_uuid: str = Column(String, ForeignKey('jobs.uuid',ondelete="CASCADE",onupdate="CASCADE"), nullable=False)
    job = relationship("Job", foreign_keys=[job_uuid], uselist=False)

    status:str = Column(String, index=True, nullable=False,default="CREATED")
    
    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<NurseryJobs: uuid: {} nursery_uuid: {} job_uuid: {} status: {}>'.format(self.uuid, self.nursery_uuid, self.job_uuid,self.status)

@event.listens_for(NurseryJobs, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()

@event.listens_for(NurseryJobs, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()


@dataclass
class GroupTeams(Base):
    """
     database model for storing Membership and Nursery related details.
    """    
    __tablename__ ='group_teams'
    uuid: str = Column(String, primary_key=True, unique=True,index = True)
    team_uuid: str = Column(String, ForeignKey('teams.uuid',ondelete = "CASCADE",onupdate= "CASCADE"), nullable=False)
    team = relationship("Team",foreign_keys=[team_uuid],uselist=False)

    group_uuid: str = Column(String, ForeignKey('groups.uuid',ondelete = "CASCADE",onupdate= "CASCADE"), nullable=False)
    group = relationship("Group",foreign_keys=[group_uuid],uselist=False)
    
    status:str = Column(types.Enum(TeamStatusEnum), index=True, nullable=False, default = TeamStatusEnum.ACTIVED)

    date_added: datetime = Column(DateTime, nullable=False, default=datetime.now())
    date_modified: datetime = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<GroupTeams: uuid: {} team_uuid: {} group_uuid: {} status: {}>'.format(self.uuid, self.team_uuid, self.group_uuid,self.status)


@event.listens_for(GroupTeams, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the creation/modified field accordingly."""
    target.date_added = datetime.now()
    target.date_modified = datetime.now()

@event.listens_for(GroupTeams, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """ Event listener that runs before a record is updated, and sets the modified field accordingly."""
    target.date_modified = datetime.now()
