import os
from app.config.constants import ConfigConstants
from app.db.db_operations import insert_detail_log, insert_process_status
from app.db.db_engine import get_db_engine, get_session, SessionLocal
from datetime import datetime
from app.utils.custom_logger import general_logger, error_logger
import sys

session = SessionLocal

print(f"Folder Manager Session: {session}")
def create_logs_folder_structure():
    """Create the logs folder structure."""
    try:
        if not os.path.exists(ConfigConstants.LOGS_FOLDER):
            os.makedirs(ConfigConstants.LOGS_FOLDER, exist_ok=True)
            general_logger.info(f"Created logs folder: {ConfigConstants.LOGS_FOLDER}")
        else:
            general_logger.info(f"Logs folder already exists: {ConfigConstants.LOGS_FOLDER}")
    except Exception as e:
        e_type, e_obj, e_tb = sys.exc_info()
        print((str(e_tb.tb_lineno)))
        print('Exception Line Number - {0} , Exception Message - {1}'.format(str(e_tb.tb_lineno),e.__str__()))
        insert_detail_log(session, "Axis Finance Bank Reconciliation Process", "Axis Finance BRS Task", "Application Name",
                            'deepak.soni@ag-technologies.com', f'{(str(e_tb.tb_lineno))}', f"{e.__str__()}", loglevel="Failed")
        insert_process_status(session, datetime.now(), "Axis Finance Bank Reconciliation Process",
                            "Axis Finance BRS Task", "Application Name", 'deepak.soni@ag-technologies.com', "Failed", f"{e.__str__()}")
        error_logger.error(f"Error while creating logs folder: {e}")
        raise


def create_folder_structure():
    """Creates the required folder structure for the project if it doesn't exist."""
    try:
        # List of main folders to create
        base_folders_to_create = [
            ConfigConstants.INPUT_FOLDER,
            ConfigConstants.OUTPUT_FOLDER,
            ConfigConstants.LOGS_FOLDER,
            ConfigConstants.TEMPLATE_FOLDER,
        ]

        # Use the imported subfolder list from folder_config
        subfolders_to_create = ConfigConstants.SUBFOLDERS
        
        for folder in base_folders_to_create:
            if not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
                general_logger.info(f"Created folder: {folder}")
            else:
                general_logger.info(f"Folder already exists: {folder}")

        # Create the subfolders inside INPUT and OUTPUT folders
        for subfolder in subfolders_to_create:
            input_subfolder = os.path.join(ConfigConstants.INPUT_FOLDER, subfolder)
            output_subfolder = os.path.join(ConfigConstants.OUTPUT_FOLDER, subfolder)

            if not os.path.exists(input_subfolder):
                os.makedirs(input_subfolder, exist_ok=True)
                general_logger.info(f"Created folder: {input_subfolder}")
            else:
                general_logger.info(f"Folder already exists: {input_subfolder}")

            if not os.path.exists(output_subfolder):
                os.makedirs(output_subfolder, exist_ok=True)
                general_logger.info(f"Created folder: {output_subfolder}")
            else:
                general_logger.info(f"Folder already exists: {output_subfolder}")
        print(f"Folder Manager - Session before insert_detail_log: {session}")
        insert_detail_log(session, "Axis Finance Bank Reconciliation Process", "Axis Finance BRS Task", "N/A",
                            'deepak.soni@ag-technologies.com', f'N/A', f"Created Folder Structure", loglevel="Info")
        insert_process_status(session, datetime.now(), "Axis Finance Bank Reconciliation Process",
                            "Axis Finance BRS Task", "N/A", 'deepak.soni@ag-technologies.com', "Info", f"Created Folder Structure")

        

    except Exception as e:
        e_type, e_obj, e_tb = sys.exc_info()
        print((str(e_tb.tb_lineno)))
        print('Exception Line Number - {0} , Exception Message - {1}'.format(str(e_tb.tb_lineno),e.__str__()))
        insert_detail_log(session, "Axis Finance Bank Reconciliation Process", "Axis Finance BRS Task", "N/A",
                            'deepak.soni@ag-technologies.com', f'{(str(e_tb.tb_lineno))}', f"{e.__str__()}", loglevel="Failed")
        insert_process_status(session, datetime.now(), "Axis Finance Bank Reconciliation Process",
                            "Axis Finance BRS Task", "N/A", 'deepak.soni@ag-technologies.com', "Failed", f"{e.__str__()}")
        error_logger.error(f"Error while creating folder structure: {e}")
        raise
