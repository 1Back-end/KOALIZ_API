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
from app.main.core.mail import send_unpaid_invoice_email
from app.main.core.security import create_access_token, generate_code, get_password_hash, verify_password, is_valid_password, \
    decode_access_token
from app.main.core.config import Config
from app.main.schemas.user import UserProfileResponse
from app.main.utils.helper import check_pass, generate_randon_key

router = APIRouter(prefix="/send-email", tags=["send-email"])

@router.post("/send-email", response_model=schemas.Msg)
def send_unpaid_email(
    input: schemas.InvoiceEmailRequest,
    db: Session = Depends(get_db)  # Utilisé pour la gestion de la base de données si nécessaire
):
    try:
        # Appel de la fonction d'envoi d'email
        send_unpaid_invoice_email(
            email_to=input.email_to,
            invoice_number=input.invoice_number,
            recipient_name=input.recipient_name,
            company_name=input.company_name,
            company_address=input.company_address,
            contact_phone=input.contact_phone,
            contact_email=input.contact_email
        )
        return schemas.Msg(message="Email sent successfully")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")