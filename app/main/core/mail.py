from datetime import datetime
import logging
from pathlib import Path
from typing import Any, Dict
import emails
from emails.template import JinjaTemplate
from sqlalchemy import or_
from app.main import models
from app.main.core.config import Config
from app.main.core.i18n import get_language, __
from app.main.models.db.session import SessionLocal
from app.main.worker import celery
import requests
import json
import uuid
import os
from app.main.utils.uploads import upload_file
from urllib.parse import urlparse
from urllib.request import urlopen
from dateutil.relativedelta import relativedelta
from dateutil import parser




def create_pdf(data, endpoint):
    headers = {"Content-Type": "application/json"}
    res = requests.post(Config.GENERATOR_PDF_URL + endpoint, data=json.dumps(data), headers=headers, stream=True)
    if res.status_code == 200:
        filename = data["iban"] if "iban" in data else str(uuid.uuid4())
        file_path = os.path.join(Config.UPLOADED_FILE_DEST, f"{filename}.pdf")
        with open(file_path, 'wb') as f:
            f.write(res.content)
        minio_url, minio_file_name, filename = upload_file(file_path, f"{filename}.pdf", "", "application/pdf")
        print(minio_url)
        return {"status": "success", "minio_url": minio_url, "url": file_path, "filename": filename}
    else:
        return {"status": "fail", "error": res}


@celery.task(name="send_email")
def send_email(
        email_to: str,
        subject_template: str = "",
        html_template: str = "",
        environment: Dict[str, Any] = {},
        file: Any = []
) -> None:
    assert Config.EMAILS_ENABLED, "aucune configuration fournie pour les variables de messagerie"
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(Config.EMAILS_FROM_NAME, Config.EMAILS_FROM_EMAIL)
    )
    for attachment in file:
        message.attach(data=open(attachment, 'rb'), filename=attachment.split("/")[-1])

    smtp_options = {"host": Config.SMTP_HOST, "port": Config.SMTP_PORT}
    if Config.SMTP_TLS:
        smtp_options["tls"] = Config.SMTP_TLS
    if Config.SMTP_SSL:
        smtp_options["ssl"] = Config.SMTP_SSL
    if Config.SMTP_USER:
        smtp_options["user"] = Config.SMTP_USER
    if Config.SMTP_PASSWORD:
        smtp_options["password"] = Config.SMTP_PASSWORD
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logging.info(f"résultat de l'email envoyé: {response}")



def send_test_email(email_to: str) -> None:
    project_name = Config.EMAIL_PROJECT_NAME
    subject = f"{project_name} - Test email"
    with open(Path(Config.EMAIL_TEMPLATES_DIR) / "test_email.html") as f:
        template_str = f.read()
    task = send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={"project_name": Config.EMAIL_PROJECT_NAME, "email": email_to},
    )
    logging.info(f"new send mail task with id {task.id}")
    

def send_reset_password_email(email_to: str, code: str, prefered_language: str, name: str) -> None:
    if str(prefered_language) in ["en", "EN", "en-EN"]:
        subject = f"SuitsMen Paris | Password reset"

        with open(Path(Config.EMAIL_TEMPLATES_DIR) / "reset_password_en.html") as f:
            template_str = f.read()
    else:
        subject = f"SuitsMen Paris | Réinitialisation de mot de passe"

        with open(Path(Config.EMAIL_TEMPLATES_DIR) / "reset_password.html") as f:
            template_str = f.read()

    task = send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "code": code,
            "name": name,
            "email": email_to
        },
    )
    # logging.info(f"new send mail task with id {task.id}")

def send_account_creation_email(email_to: str,prefered_language: str, name: str,password:str, login_link: str) -> None:
    project_name = Config.EMAIL_PROJECT_NAME
    if str(prefered_language) in ["en", "EN", "en-EN"]:
        subject = f"KOALIZZ | Account created"
    else:
        subject = f"KOALIZZ | Compte créé"

    template_path = get_template_path_based_on_lang(prefered_language)
    with open(Path(template_path) / "account_created.html") as f:
        template_str = f.read()

    task = send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": project_name,
            "password": password,
            "name": name,
            "email": email_to,
            "login_link": login_link
        }
    )

def get_template_path_based_on_lang(lang: str = "fr"):
    if not lang:
        lang = get_language()
    if lang not in ["en", "fr"]:
        lang = "fr"
    return f"{Config.EMAIL_TEMPLATES_DIR}/{lang}"


def send_reset_password_email(email_to: str, name: str, token: str, valid_minutes: int = None) -> None:
    project_name = Config.EMAIL_PROJECT_NAME
    subject = f'{project_name} - {__("mail-subject-reset-password")} {name}'

    template_path = get_template_path_based_on_lang()
    with open(Path(template_path) / "reset_password.html") as f:
        template_str = f.read()

    print("=====================================")
    task = send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": Config.EMAIL_PROJECT_NAME,
            "name": name,
            "email": email_to,
            "valid_hours": Config.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "valid_minutes": valid_minutes,
            "code": token,
        },
    )
    print("----------------------------------------")
    logging.info(f"new send mail task with id {task}")


def send_password_reset_succes_email(email_to: str, name: str, token: str) -> None:
    project_name = Config.EMAIL_PROJECT_NAME
    subject = f'{project_name} - {__("mail-subject-password-reset-succes")} {name}'

    template_path = get_template_path_based_on_lang()
    with open(Path(template_path) / "password_reset_success.html") as f:
        template_str = f.read()

    print("=====================================")
    task = send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": Config.EMAIL_PROJECT_NAME,
            "name": name,
            "email": email_to,
            # "valid_hours": Config.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            # "valid_minutes": valid_minutes,
            "code": token,
        },
    )
    print("----------------------------------------")
    logging.info(f"new send mail task with id {task}")


def send_account_confirmation_email(email_to: str, name: str, token: str, valid_minutes: int = None) -> None:
    project_name = Config.EMAIL_PROJECT_NAME
    subject = f'{project_name} - {__("mail-subject-account-confirmation-email")} {name}'

    template_path = get_template_path_based_on_lang()
    with open(Path(template_path) / "account_confirmation_email.html") as f:
        template_str = f.read()

    print("=====================================")
    task = send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": Config.EMAIL_PROJECT_NAME,
            "name": name,
            "email": email_to,
            "valid_hours": Config.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "valid_minutes": valid_minutes,
            "code": token,
        },
    )
    print("----------------------------------------")
    logging.info(f"new send mail task with id {task}")


def send_account_created_succes_email(email_to: str, name: str) -> None:
    project_name = Config.EMAIL_PROJECT_NAME
    subject = f'{project_name} - {__("mail-subject-account-created")} {name}'

    template_path = get_template_path_based_on_lang()
    with open(Path(template_path) / "account_created.html") as f:
        template_str = f.read()

    print("=====================================")
    task = send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": Config.EMAIL_PROJECT_NAME,
            "name": name,
            "email": email_to,
        },
    )
    print("----------------------------------------")
    logging.info(f"new send mail task with id {task}")


def send_reset_password_option2_email(email_to: str, name: str, token: str, valid_minutes: int = None,
                                          language: str = "fr", base_url: str = Config.RESET_PASSWORD_LINK) -> None:
    project_name = Config.EMAIL_PROJECT_NAME
    subject = f'{project_name} - {__("mail-subject-reset-password", language)} {name}'

    template_path = get_template_path_based_on_lang(language)
    with open(Path(template_path) / "reset_password_option2.html") as f:
        template_str = f.read()

    if not base_url:
        base_url = Config.RESET_PASSWORD_LINK

    task = send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": Config.EMAIL_PROJECT_NAME,
            "name": name,
            "email": email_to,
            "valid_hours": Config.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "valid_minutes": valid_minutes,
            "reset_password_link": f"{base_url}/{token}".format(language),
        },
    )
    logging.info(f"new send mail task with id {task}")


def admin_send_new_nursery_email(email_to: str, data: dict, language: str = "fr") -> None:
    project_name = Config.EMAIL_PROJECT_NAME
    subject = f'{project_name} - {__("new-nursery", language)}'

    template_path = get_template_path_based_on_lang(language)
    with open(Path(template_path) / "admin_new_nursery.html") as f:
        template_str = f.read()

    print("==================Start New Nursery Mail(Admin)===================")
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "user_name": data["user_name"],
            "email": email_to,
            "nursery_name": data["nursery_name"],
            "owner_name": data["creator_name"],
            "login_link": Config.ADMIN_LOGIN_LINK.format(language)
        }
    )
    print("=====================End New Nursery Mail(Admin)===========================")



def send_new_nursery_email(email_to: str, data: dict, language: str = "fr") -> None:
    project_name = Config.EMAIL_PROJECT_NAME
    subject = f'{project_name} - {__("new-nursery", language)}'

    template_path = get_template_path_based_on_lang(language)
    with open(Path(template_path) / "new_nursery.html") as f:
        template_str = f.read()

    print("==================Start New Nursery Mail===================")
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "user_name": data["user_name"],
            "email": email_to,
            "nursery_name": data["nursery_name"],
            "admin_name": data["creator_name"],
            "login_link": Config.LOGIN_LINK.format(language)
        }
    )
    print("=====================End New Nursery Mail===========================")



def admin_send_new_nursery_email(email_to: str, data: dict, language: str = "fr") -> None:
    project_name = Config.EMAIL_PROJECT_NAME
    subject = f'{project_name} - {__("new-nursery", language)}'

    template_path = get_template_path_based_on_lang(language)
    with open(Path(template_path) / "admin_new_nursery.html") as f:
        template_str = f.read()

    print("==================Start New Nursery Mail(Admin)===================")
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "user_name": data["user_name"],
            "email": email_to,
            "nursery_name": data["nursery_name"],
            "owner_name": data["creator_name"],
            "login_link": Config.ADMIN_LOGIN_LINK.format(language)
        }
    )
    print("=====================End New Nursery Mail(Admin)===========================")



def send_new_nursery_email(email_to: str, data: dict, language: str = "fr") -> None:
    project_name = Config.EMAIL_PROJECT_NAME
    subject = f'{project_name} - {__("new-nursery", language)}'

    template_path = get_template_path_based_on_lang(language)
    with open(Path(template_path) / "new_nursery.html") as f:
        template_str = f.read()

    print("==================Start New Nursery Mail===================")
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "user_name": data["user_name"],
            "email": email_to,
            "nursery_name": data["nursery_name"],
            "admin_name": data["creator_name"],
            "login_link": Config.LOGIN_LINK.format(language)
        }
    )
    print("=====================End New Nursery Mail===========================")


def send_unpaid_invoice_email(email_to: str, invoice_number: str,
                              recipient_name: str, company_name: str, company_address: str,
                              contact_phone: str, contact_email: str, language: str = "fr"):
    
    project_name = Config.EMAIL_PROJECT_NAME
    subject = f'{project_name} - {__("invoice-unpaid-subject", language)}'

    # Récupérer le chemin du template en fonction de la langue
    template_path = get_template_path_based_on_lang(language)
    with open(Path(template_path) / "invoice_unpaid2.html", "r", encoding="utf-8") as f:
        template_str = f.read()

    # Envoyer l'email
    task = send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": project_name,
            "invoice_number": invoice_number,
            "recipient_name": recipient_name,
            "company_name": company_name,
            "company_address": company_address,
            "contact_phone": contact_phone,
            "contact_email": contact_email
        }
    )
    
    logging.info(f"New email task created with ID {task}")



def send_absence_report_email(email_to: str, reporter_name: str, child_name: str,
                              absence_start: datetime, absence_end: datetime,
                              family_member_link: str, contact_name: str, contact_phone: str,language: str = "fr"):
    
    project_name = Config.EMAIL_PROJECT_NAME
    subject = f'{project_name} - {__("absence_report", language)}'


    template_path = get_template_path_based_on_lang(language)
    with open(Path(template_path) / "absence_report.html", "r", encoding="utf-8") as f:
        template_str = f.read()

    task = send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": project_name,
            "reporter_name": reporter_name,
            "child_name": child_name,
            "absence_start": absence_start.strftime("%d/%m/%Y %H:%M"),
            "absence_end": absence_end.strftime("%d/%m/%Y %H:%M"),
            "family_member_link": family_member_link,
            "contact_name": contact_name,
            "contact_phone": contact_phone
            # Add any other variables you need in the email template
            }
    )
    
    logging.info(f"Nouvelle tâche d'email créée avec l'ID {task}")

def send_absence_notification(parent_email: str,child_name: str, start_time: str, end_time: str,parent_name: str, contact_email: str, contact_phone: str,language: str = "fr"):

    project_name = Config.EMAIL_PROJECT_NAME
    subject = f'{project_name} - {__("absence-notification", language)}'


    template_path = get_template_path_based_on_lang(language)
    with open(Path(template_path) / "absence_notification.html", "r", encoding="utf-8") as f:
        template_str = f.read()

    task = send_email(
        email_to=parent_email,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": project_name,
            "child_name": child_name,
            "start_time": start_time,
            "end_time": end_time,
            "parent_name": parent_name,
            "contact_email": contact_email,
            "contact_phone": contact_phone
            # Add any other variables you need in the email template
            }
    )
    
    logging.info(f"Nouvelle tâche d'email créée avec l'ID {task}")

def send_delay_notification(parent_email: str, child_name: str, delay_duration: str,
                            parent_name: str, contact_email: str, contact_phone: str,
                            family_member_link: str, company_name: str, company_address: str, language: str = "fr"):
    project_name = Config.EMAIL_PROJECT_NAME
    subject = f'{project_name} - Notification de Retard'

    template_path = get_template_path_based_on_lang(language)
    with open(Path(template_path) / "delay_notification.html", "r", encoding="utf-8") as f:
        template_str = f.read()

    task = send_email(
        email_to=parent_email,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": project_name,
            "child_name": child_name,
            "delay_duration": delay_duration,
            "parent_name": parent_name,
            "contact_email": contact_email,
            "contact_phone": contact_phone,
            "family_member_link": family_member_link,
            "company_name": company_name,
            "company_address": company_address
        }
    )

    logging.info(f"Nouvelle tâche d'email créée avec l'ID {task}")