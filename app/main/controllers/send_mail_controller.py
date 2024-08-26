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
from app.main.core.mail import send_unpaid_invoice_email,send_absence_report_email,send_absence_notification,send_delay_notification
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
            language=input.language
        )
        return schemas.Msg(message="Email envoyé avec succès.")
    except Exception as e:
        # Log l'erreur avec plus de détails
        logging.error(f"Échec de l'envoi de l'email pour la notification de retard du {input.child_name} à {input.parent_email}: {e}")
        raise HTTPException(status_code=500, detail="Échec de l'envoi de l'email. Veuillez réessayer plus tard.")