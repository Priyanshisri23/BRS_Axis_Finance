import shutil
import traceback
import os
from db.db_operations import insert_detail_log
from utils.custom_logger import general_logger, error_logger

process_name="Axis Finance Bank Reconciliation Statement"
def copy_folder(source_folder, destination_folder, session, email_to):
    """
    Copies contents from the source folder to the destination folder.
    """
    try:
        if os.path.exists(destination_folder):
            shutil.rmtree(destination_folder)
            
        shutil.copytree(source_folder, destination_folder)
        print('Folder funciton')
        general_logger.info(f"Folder copied from {source_folder} to {destination_folder}")
        insert_detail_log(session, "Folder copy successful", process_name, "N/A", email_to, "N/A",
                            f"Copied input files from {source_folder} to {destination_folder}", "info")
    except FileExistsError:
        general_logger.warning(f"The destination folder {destination_folder} already exists.")
    except Exception as e:
        error_message = f"Failed to copy folder from {source_folder} to {destination_folder}: {e}"
        error_logger.error(error_message)
        print(e)
        traceback.print_exc()
        raise