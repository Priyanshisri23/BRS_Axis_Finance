# import sys
# sys.path.append('.')
import os
from datetime import datetime
from app.utils.excel_utils import get_excel_data

class ConfigConstants:
    """Centralized configuration constants for file paths and default values."""

    # Base paths
    # ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    ROOT_DIR_ENV = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    ASSET_FOLDER = os.path.join(ROOT_DIR, "assets")

    # Client-specific configuration file
    CONFIG_FILE_PATH = os.path.join(ASSET_FOLDER, 'client', 'client_config.xlsx')

    # Current date for dynamic folder creation (year, month, date)
    CURRENT_DATE = datetime.now().strftime("%d-%m-%Y")
    CURRENT_YEAR = datetime.now().strftime("%Y")
    CURRENT_MONTH = datetime.now().strftime("%B")

    # Subdirectories under asset folder
    CLIENT_FOLDER = os.path.join(ASSET_FOLDER, "client")

    # Input structure
    INPUT_FOLDER = os.path.join(ASSET_FOLDER, "input", CURRENT_YEAR, CURRENT_MONTH, CURRENT_DATE)
    # SHARED_FOLDER = os.path.join(INPUT_FOLDER, "shared_files")

    # Output structure
    OUTPUT_FOLDER = os.path.join(ASSET_FOLDER, "output", CURRENT_YEAR, CURRENT_MONTH, CURRENT_DATE)

    # Template folder
    TEMPLATE_FOLDER = os.path.join(ROOT_DIR, 'app', "templates")
    # print('template folder', TEMPLATE_FOLDER)

    # Log structure (organized by year/month/date)
    LOGS_FOLDER = os.path.join(ROOT_DIR, "logs", CURRENT_YEAR, CURRENT_MONTH, CURRENT_DATE)

    config_data = get_excel_data(CONFIG_FILE_PATH)
    DEFAULT_EMAIL_TO = config_data.get('email_to')
    DEFAULT_EMAIL_CC = config_data.get('email_cc')
    ERROR_EMAIL_SUBJECT = "Axis Finance BRS Bot - Error"
    SUCCESS_EMAIL_SUBJECT = "Axis Finance BRS Bot - Success"

    # Log file names
    GENERAL_LOG_NAME = "general_log.txt"
    ERROR_LOG_NAME = "error_log.txt"

    # Path to log files
    GENERAL_LOG_PATH = os.path.join(LOGS_FOLDER, GENERAL_LOG_NAME)
    ERROR_LOG_PATH = os.path.join(LOGS_FOLDER, ERROR_LOG_NAME)


    

    # Subfolder names for the input and output folders
    SUBFOLDER_669 = '669'
    SUBFOLDER_8350 = '8350'
    SUBFOLDER_9791 = '9197'
    SUBFOLDER_7687 = '7687'
    SUBFOLDER_86033 = '6033'
    SUBFOLDER_8607 = '607'

    # List of subfolder variables
    SUBFOLDERS = [SUBFOLDER_669, SUBFOLDER_8350, SUBFOLDER_9791, SUBFOLDER_7687, SUBFOLDER_86033, SUBFOLDER_8607]



# For debugging purposes
if __name__ == "__main__":
    print("Root Directory:", ConfigConstants.ROOT_DIR)
    print("Asset Folder:", ConfigConstants.ASSET_FOLDER)
    print("Input Folder (Date-based):", ConfigConstants.INPUT_FOLDER)
    print("Output Folder (Date-based):", ConfigConstants.OUTPUT_FOLDER)
    # print("FTP Download Folder:", ConfigConstants.FTP_DOWNLOAD_FOLDER)
    # print("Shared Folder:", ConfigConstants.SHARED_FOLDER)
    print("Logs Folder (Date-based):", ConfigConstants.LOGS_FOLDER)
