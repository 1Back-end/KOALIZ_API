from datetime import datetime, date
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict, EmailStr, Json

from app.main.schemas import DataList
from app.main.schemas.role import RoleBase


class AddedBy(BaseModel):
    uuid: str
    email: EmailStr
    firstname: Optional[str]
    lastname: str

    model_config = ConfigDict(from_attributes=True)

class Login(BaseModel):
    email: EmailStr
    password: str


class ResetPasswordStep1(BaseModel):
    email: EmailStr
    new_password: str


class ResetPasswordStep2(BaseModel):
    email: EmailStr
    otp: str


class ResetPasswordOption2Step1(BaseModel):
    email: EmailStr
    language: str = "fr"


class ResetPasswordOption2Step2(BaseModel):
    new_password: str
    token: str


class UserBase(BaseModel):
    email: EmailStr
    firstname: str
    lastname: str
    is_new_user: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)

class ValidateAccount(BaseModel):
    token: str
    email:EmailStr

class User(UserBase):
    uuid: Optional[str] = None
    date_added: datetime
    date_modified: datetime


class Storage(BaseModel):
    uuid: Optional[str] = None
    file_name: Optional[str] = None
    url: Optional[str] = None
    mimetype: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    size: Optional[int] = None
    thumbnail: Any = None
    medium: Any = None
    date_added: Optional[datetime] = None
    date_modified: Optional[datetime] = None


class UserProfileResponse(UserBase):
    uuid: Optional[str] = None
    role: RoleBase
    date_added: datetime
    date_modified: datetime
    avatar: Optional[Storage] = None



class UserDetail(User):
    uuid: str
    avatar: Optional[Storage] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    pass


class UserList(DataList):
    data: List[User] = []


class UserUpdate(BaseModel):
    user_uuid: str
    country_code: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    birthday: Optional[date] = None
    storage_uuid: str = None


class InvoiceEmailRequest(BaseModel):
    email_to: str
    invoice_number: str
    recipient_name: str
    company_name: str
    company_address: str
    contact_phone: str
    contact_email: str
    # language: str = "fr"
    model_config = ConfigDict(from_attributes=True)


class AbsenceReportRequest(BaseModel):
    reporter_name: str
    child_name: str
    absence_start: datetime
    absence_end: datetime
    family_member_link: str
    contact_name: str
    contact_phone: str
    contact_email: str
    # language: str = "fr"
    model_config = ConfigDict(from_attributes=True)

class DelayNotificationRequest(BaseModel):
    parent_email: EmailStr
    child_name: str
    delay_duration: str
    parent_name: str
    contact_email: EmailStr
    contact_phone: str
    family_member_link: str
    company_name: str
    company_address: str
    # language: str = "fr"  # Valeur par défaut "fr"
    model_config = ConfigDict(from_attributes=True)

class VaccinationReminderRequest(BaseModel):
    parent_name: str
    parent_email: EmailStr
    child_name: str
    vaccine_name: str
    due_date: str  # Vous pouvez aussi utiliser `datetime.date` pour une meilleure gestion des dates
    child_profile_link: str
    # language: str = "fr"  # Valeur par défaut


class OccasionalCareRequest(BaseModel):
    parent_name: str
    parent_email: EmailStr
    child_name: str
    care_date: str  # Utilisez `datetime.date` si vous gérez les dates en format ISO
    start_time: str  # Vous pouvez utiliser `datetime.time` pour les heures
    end_time: str  # Idem ici pour les heures
    parent_profile_link: str
    company_name: str 
    company_address: str 
    contact_phone: str 
    contact_email: str 
    # language: str = "fr"  # Valeur par défaut

class OpeningNotificationRequest(BaseModel):
    recipient_name: str  # Le nom du destinataire de l'email
    recipient_email: EmailStr  # Email du destinataire
    micro_creche_name: str 
    location: str 
    address: str 
    contact_phone: str
    contact_email: EmailStr
    # language: str = "fr"  # Langue par défaut

class PreEnrollmentRequest(BaseModel):
    first_parent_name: str
    first_parent_email: EmailStr
    second_parent_name: str
    second_parent_email: EmailStr
    child_age_at_entry: str
    contract_start_date: str
    dossier_link: str
    contact_name: str 
    contact_address: str
    contact_phone: str
    contact_email: EmailStr 
    # language: str = "fr"  # Langue par défaut

class ParentMessageRequest(BaseModel):
    parent_name: str
    child_name: str
    message_content: str
    timestamp: str
    recipient_email: str

class DelayNotificationRequestEmail(BaseModel):
    parent_name: str
    child_name: str
    delay_minutes: int
    recipient_email: str

class AbsenceNotification(BaseModel):
    parent_name: str
    child_name: str
    absence_start: str  # Format: YYYY-MM-DDTHH:MM:SS
    absence_end: str    # Format: YYYY-MM-DDTHH:MM:SS
    recipient_email: str
