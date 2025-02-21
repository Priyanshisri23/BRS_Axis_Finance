import json
import traceback

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

from app.config.constants import ConfigConstants
from app.db.db_engine import get_session, get_db_engine
from app.db.db_operations import insert_detail_log
from app.utils.custom_logger import general_logger, error_logger


def run():
    """Loads the configuration from the Excel file and returns it as a dictionary."""
    session = None
    try:
        # session = get_session(get_db_engine())
        session = get_session()


        # Load configuration from Excel file
        df = pd.read_excel(ConfigConstants.CONFIG_FILE_PATH, header=0, index_col=0)
        config_data = {index: value for index, value in df.iloc[:, 0].items()}

        # Convert the configuration data to a dictionary (handles JSON string conversion)
        config_dict = json.loads(json.dumps(config_data))
        # print('<><><>S', config_dict['shared_folder_path'])
        # Log successful configuration load
        general_logger.info("Configuration loaded successfully from process_configfile.xlsx.")

        return config_dict

    except FileNotFoundError as e:
        error_message = f"Configuration file not found: {ConfigConstants.CONFIG_FILE_PATH}. Error: {e}"
        error_logger.error(error_message)
        raise FileNotFoundError(error_message)

    except SQLAlchemyError as e:
        tb = traceback.format_exc()
        error_message = f"Database error during config load: {e}. Traceback: {tb}"
        error_logger.error(error_message)
        if session:
            insert_detail_log(session, "Axis Finance Bank Reconciliation Statements", "Axis Finance BRS Task", "N/A",
                              ConfigConstants.DEFAULT_EMAIL_TO, str(e), "Failed", loglevel="ERROR")
        raise SQLAlchemyError(error_message)

    except Exception as e:
        tb = traceback.format_exc()
        line_number = tb.splitlines()[-2]
        error_message = f"Unexpected error in config_loader at line {line_number}: {e}"
        error_logger.error(f"Unexpected error in config_loader: {e}. Traceback: {tb}")
        if session:
            insert_detail_log(session, "Axis Finance Bank Reconciliation Statements", "Axis Finance BRS Task", "N/A",
                              ConfigConstants.DEFAULT_EMAIL_TO, f"Line {line_number}: {e}", "Failed", loglevel="ERROR")
        raise Exception(error_message)

    # Add finally block to close the session
