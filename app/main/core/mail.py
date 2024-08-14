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
    project_name = Config.PROJECT_NAME
    subject = f"{project_name} - Test email"
    with open(Path(Config.EMAIL_TEMPLATES_DIR) / "test_email.html") as f:
        template_str = f.read()
    task = send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={"project_name": Config.PROJECT_NAME, "email": email_to},
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

def send_account_creation_email(email_to: str,prefered_language: str, name: str,password:str) -> None:
    project_name = Config.PROJECT_NAME
    if str(prefered_language) in ["en", "EN", "en-EN"]:
        subject = f"KOALIZZ | Account created succesfully."
        content = "is your password. You must change it after the first connection for better security."
        with open(Path(Config.EMAIL_TEMPLATES_DIR) / "account_creation.html") as f:
            template_str = f.read()
    else:
        subject = f"KOALIZZ | Compte créé avec succès."
        content = "est votre mot de passe.Vous avez l'obligation de le modifier aprės la première connexion pour une meilleure sécurité."

        with open(Path(Config.EMAIL_TEMPLATES_DIR) / "account_creation.html") as f:
            template_str = f.read()

    task = send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "content": content,
            "project_name": project_name,
            "password": password,
            "name": name,
            "email": email_to
        },
    )

def get_template_path_based_on_lang(lang: str = "fr"):
    if not lang:
        lang = get_language()
    if lang not in ["en", "fr"]:
        lang = "fr"
    return f"{Config.EMAIL_TEMPLATES_DIR}/{lang}"


def send_reset_password_email(email_to: str, name: str, token: str, valid_minutes: int = None) -> None:
    project_name = Config.PROJECT_NAME
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
            "project_name": Config.PROJECT_NAME,
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
    project_name = Config.PROJECT_NAME
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
            "project_name": Config.PROJECT_NAME,
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
    project_name = Config.PROJECT_NAME
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
            "project_name": Config.PROJECT_NAME,
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
    project_name = Config.PROJECT_NAME
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
            "project_name": Config.PROJECT_NAME,
            "name": name,
            "email": email_to,
        },
    )
    print("----------------------------------------")
    logging.info(f"new send mail task with id {task}")


def send_reset_password_option2_email(email_to: str, name: str, token: str, valid_minutes: int = None,
                                          language: str = "fr", base_url: str = Config.RESET_PASSWORD_LINK) -> None:
    project_name = Config.PROJECT_NAME
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
            "project_name": Config.PROJECT_NAME,
            "name": name,
            "email": email_to,
            "valid_hours": Config.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "valid_minutes": valid_minutes,
            "reset_password_link": f"{base_url}/{token}".format(language),
        },
    )
    logging.info(f"new send mail task with id {task}")
