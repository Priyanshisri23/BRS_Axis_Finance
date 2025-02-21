import datetime
import os
import smtplib
import traceback
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import FileSystemLoader, Environment
from config.constants import ConfigConstants
from config.email_constants import (
    SUBJECT_STARTED_EXECUTION, SUBJECT_COMPLETED, SUBJECT_ERROR, SUBJECT_FILE_MISSING, SUBJECT_COLUMN_MISSING,
    PROCESS_NAME,
    EMAIL_STYLES, SUBJECT_SFTP_ERROR, SUBJECT_BLANK_CAPS
)
from config.settings import Config
from utils.custom_logger import error_logger, general_logger

# Set up Jinja2 environment
template_loader = FileSystemLoader(searchpath=ConfigConstants.TEMPLATE_FOLDER)
template_env = Environment(loader=template_loader)


class EmailConfig:
    email_to = ConfigConstants.DEFAULT_EMAIL_TO
    email_cc = ConfigConstants.DEFAULT_EMAIL_CC
    smtp_server = Config.SMTP_SERVER
    smtp_port = Config.SMTP_PORT
    smtp_username = Config.SMTP_USERNAME
    smtp_password = Config.SMTP_PASSWORD
    general_logger.info(f"Email configuration loaded successfully for: {smtp_username}")


def send_email(subject, body, recipient, cc=None, attachments=None, screenshot_file=None, html=False):
    """
    Send an email with the provided subject, body, and optional attachments.
    """
    msg = MIMEMultipart()
    msg['From'] = EmailConfig.smtp_username
    msg['To'] = recipient
    msg['Cc'] = cc if cc else ""
    msg['Subject'] = subject

    # Attach the body as HTML or plain text
    if html:
        msg.attach(MIMEText(body, 'html'))
    else:
        msg.attach(MIMEText(body, 'plain'))

    # Attach files if provided
    if attachments:
        for file in attachments:
            try:
                with open(file, "rb") as attachment:
                    part = MIMEApplication(attachment.read(), Name=os.path.basename(file))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file)}"'
                msg.attach(part)
            except Exception as e:
                error_logger.error(f"Error attaching file {file}: {e}")

    # Attach screenshot if provided
    if screenshot_file:
        try:
            with open(screenshot_file, "rb") as attachment:
                part = MIMEApplication(attachment.read(), Name=os.path.basename(screenshot_file))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(screenshot_file)}"'
            msg.attach(part)
        except Exception as e:
            error_logger.error(f"Error attaching screenshot: {e}")

    # Try sending the email
    try:
        smtp_server = smtplib.SMTP(EmailConfig.smtp_server, EmailConfig.smtp_port)
        smtp_server.ehlo()  # Identify yourself to the server
        smtp_server.starttls()  # Start TLS encryption
        smtp_server.ehlo()  # Re-identify yourself after TLS
        smtp_server.login(EmailConfig.smtp_username, EmailConfig.smtp_password)

        # Send email
        smtp_server.sendmail(EmailConfig.smtp_username, recipient.split(",") + (cc.split(",") if cc else []),
                             msg.as_string())
        smtp_server.quit()
        general_logger.info(f"Email sent to {recipient}.")
    except smtplib.SMTPAuthenticationError as auth_err:
        error_logger.error(f"SMTP Authentication Error: {str(auth_err)}")
    except Exception as e:
        error_logger.error(f"Failed to send email to {recipient}: {str(e)}")
        traceback.print_exc()


# Email Notification Functions
def start_mail(file_name):
    """
    Send a start notification email.
    """
    current_time = datetime.datetime.now()
    formatted_datetime = current_time.strftime("%d-%m-%Y %H:%M:%S")
    current_year = current_time.strftime("%Y")

    # Render the HTML template with styles
    template = template_env.get_template('started_execution.html')
    body = template.render(
        process_name=PROCESS_NAME,
        file_name=file_name,
        datetime=formatted_datetime,
        current_year=current_year,
        email_styles=EMAIL_STYLES
    )
    subject = SUBJECT_STARTED_EXECUTION

    send_email(subject, body, EmailConfig.email_to, cc=EmailConfig.email_cc, html=True)


def success_mail(file_name, attachement):
    """
    Send a success notification email.
    """
    current_time = datetime.datetime.now()
    formatted_datetime = current_time.strftime("%d-%m-%Y %H:%M:%S")
    current_year = current_time.strftime("%Y")

    # Render the success HTML template with styles
    template = template_env.get_template('success_execution.html')
    body = template.render(
        process_name=PROCESS_NAME,
        file_name=file_name,
        datetime=formatted_datetime,
        current_year=current_year,
        email_styles=EMAIL_STYLES
    )
    subject = SUBJECT_COMPLETED
    
    send_email(subject, body, EmailConfig.email_to, cc=EmailConfig.email_cc, attachments=[attachement], html=True)



def error_mail(file_name, e):
    """
    Send an error notification email.
    """
    current_time = datetime.datetime.now()
    formatted_datetime = current_time.strftime("%d-%m-%Y %H:%M:%S")
    current_year = current_time.strftime("%Y")

    # Render the error HTML template with styles
    template = template_env.get_template('error_notification.html')
    body = template.render(
        process_name=PROCESS_NAME,
        file_name=file_name,
        datetime=formatted_datetime,
        error_message=str(e),
        current_year=current_year,
        email_styles=EMAIL_STYLES
    )
    subject = SUBJECT_ERROR

    send_email(subject, body, EmailConfig.email_to, cc=EmailConfig.email_cc, html=True)



def column_not_exist_mail(file_name, column_name):
    """
    Send a notification email if a required column is missing in a file.
    """
    current_time = datetime.datetime.now()
    formatted_datetime = current_time.strftime("%d-%m-%Y %H:%M:%S")
    current_year = current_time.strftime("%Y")

    # Render the column missing HTML template with styles
    template = template_env.get_template('column_not_exist.html')
    body = template.render(
        process_name=PROCESS_NAME,
        file_name=file_name,
        column_name=column_name,
        datetime=formatted_datetime,
        current_year=current_year,
        email_styles=EMAIL_STYLES
    )
    subject = SUBJECT_COLUMN_MISSING

    send_email(subject, body, EmailConfig.email_to, cc=EmailConfig.email_cc, html=True)


def file_not_exist_mail(file_name, folder_name):
    """
    Send a notification email if a required file is missing.
    """
    current_time = datetime.datetime.now()
    formatted_datetime = current_time.strftime("%d-%m-%Y %H:%M:%S")
    current_year = current_time.strftime("%Y")

    # Render the file missing HTML template with styles
    template = template_env.get_template('file_not_exist.html')
    body = template.render(
        process_name=PROCESS_NAME,
        file_name=file_name,
        folder_name=folder_name,
        datetime=formatted_datetime,
        current_year=current_year,
        email_styles=EMAIL_STYLES
    )
    subject = SUBJECT_FILE_MISSING

    send_email(subject, body, EmailConfig.email_to, cc=EmailConfig.email_cc, html=True)

def ftp_error_mail(file_name, error_message):
    """
    Send an email if there's an issue with accessing files from the FTP server.
    """
    current_time = datetime.datetime.now()
    formatted_datetime = current_time.strftime("%d-%m-%Y %H:%M:%S")
    current_year = current_time.strftime("%Y")

    # Render the FTP error HTML template with styles
    template = template_env.get_template('sftp_error.html')
    body = template.render(
        process_name=PROCESS_NAME,
        file_name=file_name,
        error_message=error_message,
        datetime=formatted_datetime,
        current_year=current_year,
        email_styles=EMAIL_STYLES
    )
    subject = SUBJECT_SFTP_ERROR

    send_email(subject, body, EmailConfig.email_to, cc=EmailConfig.email_cc, html=True)


def blank_trade_cap(file_name):
    """
    Send a notification email if a required file is missing.
    """
    current_time = datetime.datetime.now()
    formatted_datetime = current_time.strftime("%d-%m-%Y %H:%M:%S")
    current_year = current_time.strftime("%Y")

    # Render the file missing HTML template with styles
    template = template_env.get_template('blank_cap_notification.html')
    body = template.render(
        process_name=PROCESS_NAME,
        file_name=file_name,
        datetime=formatted_datetime,
        current_year=current_year,
        email_styles=EMAIL_STYLES
    )
    subject = SUBJECT_BLANK_CAPS

    send_email(subject, body, EmailConfig.email_to, cc=EmailConfig.email_cc, attachments=[file_name], html=True)


def ftp_file_not_exist_mail(file_name):
    """
    Send a notification email if a required file is missing.
    """
    current_time = datetime.datetime.now()
    formatted_datetime = current_time.strftime("%d-%m-%Y %H:%M:%S")
    ucr_date = current_time.strftime("%d-%m-%Y")
    current_year = current_time.strftime("%Y")

    # Render the file missing HTML template with styles
    template = template_env.get_template('ftp_file_not_exist.html')
    body = template.render(
        process_name=PROCESS_NAME,
        file_name=file_name,
        datetime=formatted_datetime,
        current_year=current_year,
        current_date=ucr_date,
        email_styles=EMAIL_STYLES
    )
    subject = SUBJECT_FILE_MISSING

    send_email(subject, body, EmailConfig.email_to, cc=EmailConfig.email_cc, html=True)