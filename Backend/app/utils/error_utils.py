from datetime import datetime
import sys
import traceback
from app.utils.custom_logger import error_logger
from app.init.email_service import error_mail, file_not_exist_mail
from app.db.db_operations import insert_process_status

process_name="Axis Finance Bank Reconciliation Statement"
def handle_critical_error(session, process_name, error, folder, email_to):
    """
    Handles critical errors by sending an email, logging the error, and updating the database.

    :param session: SQLAlchemy session for database interaction
    :param process_name: Name of the process where the error occurred
    :param error: The exception object
    :param folder: The folder related to the process
    :param email_to: Email address to send error notification
    """
    tb = traceback.extract_tb(error.__traceback__)
    line_number = tb[-1][1]
    error_message = f"Error in {process_name}: {error} at line {line_number}"

    # Log and send an error email
    error_logger.error(error_message)
    error_mail(process_name, error,email_to)

    # Insert the error status in the DB
    insert_process_status(session, datetime.now(), "Axis Finance Bank Reconciliation Statement process", "Axis Finance BRS task",
                          "N/A", email_to, "failed", f"{process_name} failed due to error.")

    # Exit the process
    # sys.exit(1)

def file_not_exist_email(file_name, folder_name):
    file_not_exist_mail(file_name, folder_name)


def file_not_found_error(session, process_name, folder, filename, email_to):
    error_message = f"File not found in folder {folder} for {process_name}"

    # Log and send an error email
    error_logger.error(error_message)
    
    # file_not_exist_mail(file_name=filename, folder_name=folder)


    # Insert the error status in the DB
    insert_process_status(session, datetime.now(), "Axis Finance Bank Reconciliation Statement process", "Axis Finance BRS task",
                          "N/A", email_to, "failed", f"{process_name} failed due to missing file.")

    # Exit the processr
    # sys.exit(1)
