import logging
import uuid
from datetime import timedelta, datetime
from typing import Any, Optional, List
from fastapi import APIRouter, Depends, Body, HTTPException, Query, File
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.mail import send_unpaid_invoice_email,send_absence_report_email,send_absence_notification,send_delay_notification, send_vaccination_reminder,send_occasional_care_notification,send_opening_notification,send_pre_enrollment_notification,send_parent_message_email,send_delay_notification_email,send_absence_notification_email 
from app.main.core.config import Config
from app.main.schemas.user import UserProfileResponse
from app.main.utils.helper import check_pass, generate_randon_key

router = APIRouter(prefix="/send-email", tags=["send-email"])

@router.post("/send-email", response_model=schemas.Msg)
def send_unpaid_email_endpoint(
    input: schemas.InvoiceEmailRequest,
    db: Session = Depends(get_db)
):
    """
    Envoie un email de facture impayée au destinataire spécifié.
    """
    try:
        # Appel de la fonction pour envoyer l'email
        send_unpaid_invoice_email(
            email_to=input.email_to,
            invoice_number=input.invoice_number,
            recipient_name=input.recipient_name,
            company_name=input.company_name,
            company_address=input.company_address,
            contact_phone=input.contact_phone,
            contact_email=input.contact_email,
            # language=input.language
        )
        return schemas.Msg(message="Email envoyé avec succès.")
    except Exception as e:
        # Log l'erreur avec plus de détails
        logging.error(f"Échec de l'envoi de l'email pour la facture {input.invoice_number} à {input.email_to}: {e}")
        raise HTTPException(status_code=500, detail="Échec de l'envoi de l'email. Veuillez réessayer plus tard.")
    

# @router.post("/send-absence-report-email", response_model=schemas.Msg)
# def send_absence_report_email_endpoint(
#     input: schemas.AbsenceReportRequest,
#     db: Session = Depends(get_db)
# ):
#     try:
#            # Appel de la fonction pour envoyer l'email
#         send_absence_report_email(
            
#                 email_to=input.contact_email,
#                 reporter_name=input.reporter_name,
#                 child_name=input.child_name,
#                 absence_start=input.absence_start,
#                 absence_end=input.absence_end,
#                 family_member_link=input.family_member_link,
#                 contact_name=input.contact_name,
#                 contact_phone=input.contact_phone
#         )
#         return schemas.Msg(message="Email envoyé avec succès.")
#     except Exception as e:
#         # Log l'erreur avec plus de détails
#         logging.error(f"Échec de l'envoi de l'email pour le rapport d'absence du {input.child_name} à {input.contact_email}: {e}")
#         raise HTTPException(status_code=500, detail="Échec de l'envoi de l'email. Veuillez réessayer plus tard.")
        
@router.post("/send_delay_notification_endpoint",response_model=schemas.Msg)
def send_delay_notification_endpoint(
    input: schemas.DelayNotificationRequest,
    db: Session = Depends(get_db)
):
    try:
        # Appel de la fonction pour envoyer l'email
        send_delay_notification(
            parent_email=input.parent_email,
            child_name=input.child_name,
            delay_duration=input.delay_duration,
            parent_name=input.parent_name,
            contact_email=input.contact_email,
            contact_phone=input.contact_phone,
            family_member_link=input.family_member_link,
            company_name=input.company_name,
            company_address=input.company_address,
            # language=input.language
        )
        return schemas.Msg(message="Email envoyé avec succès.")
    except Exception as e:
        # Log l'erreur avec plus de détails
        logging.error(f"Échec de l'envoi de l'email pour la notification de retard du {input.child_name} à {input.parent_email}: {e}")
        raise HTTPException(status_code=500, detail="Échec de l'envoi de l'email. Veuillez réessayer plus tard.")
    
@router.post("/send_vaccination_reminder", response_model=schemas.Msg)
def send_vaccination_reminder_endpoint(
    input: schemas.VaccinationReminderRequest,
    db: Session = Depends(get_db)
):
    try:
        send_vaccination_reminder(
            parent_name=input.parent_name,
            parent_email=input.parent_email,
            child_name=input.child_name,
            vaccine_name=input.vaccine_name,
            due_date=input.due_date,
            child_profile_link=input.child_profile_link,
            # language=input.language
        )
        return schemas.Msg(message="Email envoyé avec succès.")
    except Exception as e:
        # Log l'erreur avec plus de détails
        logging.error(f"Échec de l'envoi de l'email pour le rappel de vaccination pour le {input.child_name} à {input.parent_email}: {e}")
        raise HTTPException(status_code=500, detail="Échec de l'envoi de l'email. Veuillez réessayer plus tard.")
    
    
@router.post("/send_occasional_care_notification", response_model=schemas.Msg)
async def send_occasional_care_notification_endpoint(
    input: schemas.OccasionalCareRequest,
    db: Session = Depends(get_db)  # Si vous n'utilisez pas de DB, vous pouvez enlever cette dépendance
):
    try:
        send_occasional_care_notification(
            parent_name=input.parent_name,
            parent_email=input.parent_email,
            child_name=input.child_name,
            care_date=input.care_date,
            start_time=input.start_time,
            end_time=input.end_time,
            parent_profile_link=input.parent_profile_link,
            company_name=input.company_name,
            company_address=input.company_address,
            contact_phone=input.contact_phone,
            contact_email=input.contact_email,
            # language=input.language
        )
        return schemas.Msg(message="Email envoyé avec succès.")
    except Exception as e:
        # Log l'erreur avec plus de détails
        logging.error(f"Échec de l'envoi de l'email pour la notification d'occasionnelle de soins pour le {input.child_name} à {input.parent_email}: {e}")
        raise HTTPException(status_code=500, detail="Échec de l'envoi de l'email. Veuillez réessayer plus tard.")

@router.post("/send_opening_notification", response_model=schemas.Msg)
async def send_opening_notification_endpoint(
    input: schemas.OpeningNotificationRequest,
    db: Session = Depends(get_db)  # Si une base de données n'est pas nécessaire, supprimez ceci
):
    try:
        send_opening_notification(
            recipient_name=input.recipient_name,
            recipient_email=input.recipient_email,
            micro_creche_name=input.micro_creche_name,
            location=input.location,
            address=input.address,
            contact_phone=input.contact_phone,
            contact_email=input.contact_email,
            # language=input.language
        )
        return schemas.Msg(message="Email envoyé avec succès.")
    except Exception as e:
        # Log l'erreur avec plus de détails
        logging.error(f"Échec de l'envoi de l'email pour la notification d'ouverture de la micro-crèche pour {input.micro_creche_name}: {e}")
        raise HTTPException(status_code=500, detail="Échec de l'envoi de l'email. Veuillez réessayer plus tard.")

@router.post("/send_pre_enrollment_notification", response_model=schemas.Msg)
async def send_pre_enrollment_notification_endpoint(
    input: schemas.PreEnrollmentRequest,
    db: Session = Depends(get_db)
):
    try:
        send_pre_enrollment_notification(
            first_parent_name=input.first_parent_name,
            first_parent_email=input.first_parent_email,
            second_parent_name=input.second_parent_name,
            second_parent_email=input.second_parent_email,
            child_age_at_entry=input.child_age_at_entry,
            contract_start_date=input.contract_start_date,
            dossier_link=input.dossier_link,
            contact_name=input.contact_name,
            contact_address=input.contact_address,
            contact_phone=input.contact_phone,
            contact_email=input.contact_email,
            # language=input.language
        )
        return schemas.Msg(message="Email envoyé avec succès.")
    except Exception as e:
        # Log l'erreur avec plus de détails
        logging.error(f"Échec de l'envoi de l'email pour la notification d'inscription préliminaire pour le {input.child_age_at_entry} ans: {e}")
        raise HTTPException(status_code=500, detail="Échec de l'envoi de l'email. Veuillez réessayer plus tard.")
    
@router.post("/send-parent-message",response_model=schemas.Msg)
def send_parent_message_endpoint(
    input: schemas.ParentMessageRequest,
    db: Session = Depends(get_db)
):
    try:
        send_parent_message_email(
            email_to=input.recipient_email,
            parent_name=input.parent_name,
            child_name=input.child_name,
            message_content=input.message_content,
            timestamp=input.timestamp
        )
        return schemas.Msg(message="Email envoyé avec succès.")
    except Exception as e:
        # Log l'erreur avec plus de détails
        logging.error(f"Échec de l'envoi de l'email pour la notification de message parent à {input.recipient_email}: {e}")
        raise HTTPException(status_code=500, detail="Échec de l'envoi de l'email. Veuillez réessayer plus tard.")
    
@router.post("/send-delay-notification",response_model=schemas.Msg)
def send_delay_notification_endpoint(
    input: schemas.DelayNotificationRequestEmail,
    db: Session = Depends(get_db)
):
    try:
        send_delay_notification_email(
            email_to=input.recipient_email,
            parent_name=input.parent_name,
            child_name=input.child_name,
            delay_minutes=input.delay_minutes
        )
        return schemas.Msg(message="Email envoyé avec succès.")
    except Exception as e:
        # Log l'erreur avec plus de détails
        logging.error(f"Échec de l'envoi de l'email pour la notification de retard à {input.recipient_email}: {e}")
        raise HTTPException(status_code=500, detail="Échec de l'envoi de l'email. Veuillez réessayer plus tard.")
    
@router.post("/notify-absence",response_model=schemas.Msg)

def notify_absence_endpoint(
    input: schemas.AbsenceNotification,
    db: Session = Depends(get_db)
):
    try:
        send_absence_notification_email(
             parent_name=input.parent_name,
            child_name=input.child_name,
            absence_start=input.absence_start,
            absence_end=input.absence_end,
            recipient_email=input.recipient_email
        )
        return schemas.Msg(message="Email envoyé avec succès.")
    except Exception as e:
        # Log l'erreur avec plus de détails
        logging.error(f"Échec de l'envoi de l'email pour la notification d'absence pour {input.child_name} à {input.recipient_email}: {e}")
        raise HTTPException(status_code=500, detail="Échec de l'envoi de l'email. Veuillez réessayer plus tard.")