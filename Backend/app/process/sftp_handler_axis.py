import paramiko
import os
import time
import re
from dotenv import load_dotenv
from app.init.config_loader import run as load_config
from app.config.constants import ConfigConstants
from pathlib import Path
from app.db.db_engine import SessionLocal
from app.db.db_operations import insert_detail_log, insert_process_status

config_data = load_config()
# SFTP server details
# hostname = "10.9.129.47"
# port = 22  # Default SFTP port
# username = "SAP_Treasury"
# password = "Mumbai#2025"

#Load enviroment from .env
load_dotenv(ConfigConstants.ROOT_DIR_ENV + "/.env")
session = SessionLocal
hostname = os.getenv("FTP_HOST")
port = os.getenv("FTP_PORT")
username = os.getenv("SFTP_USERNAME")
password = os.getenv("SFTP_PASSWORD")


def sftp_hander(account_no):
    insert_detail_log(session, "Axis Finance Bank Reconciliation Process", "Axis Finance BRS Task", "N/A",
                            'BRS.AutoMail@axisfinance.in', f'N/A', f"Establishing connect with SFTP for downloading file", loglevel="Info")
    base_path = "/BRS_UAT/Bank Reco"
    accounts = [account_no]
    remote_folders = [f"{base_path} {account}/Input Files" for account in accounts]
    # Local directory to save the downloaded files
    local_directory =  Path(ConfigConstants.INPUT_FOLDER)
    # Ensure the local directory exists
    os.makedirs(local_directory, exist_ok=True)
    # Retry configuration
    max_retries = 3
    delay_between_retries = 5  # seconds
    ssh = None
    sftp = None
    try:
        # Retry logic for connecting to the SFTP server
        for attempt in range(1, max_retries + 1):
            try:
                print(f"Attempt {attempt} to connect to the SFTP server...")
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname, port, username, password)
                sftp = ssh.open_sftp()
                print("Connected to the SFTP server successfully.")
                break
            except Exception as conn_err:
                print(f"Connection attempt {attempt} failed: {conn_err}")
                if attempt < max_retries:
                    print(f"Retrying in {delay_between_retries} seconds...")
                    time.sleep(delay_between_retries)
                else:
                    insert_detail_log(session, "Axis Finance Bank Reconciliation Process", "Axis Finance BRS Task", "N/A",
                            'BRS.AutoMail@axisfinance.in', f'N/A', f"Failed to connect to the SFTP server after multiple attempts", loglevel="Failed")
                    raise Exception("Failed to connect to the SFTP server after multiple attempts.")

        # Iterate through each remote folder
        for folder in remote_folders:
            path_parts = folder.strip('/').split('/')
            if len(path_parts) > 1:
                print('IF_Len', len(path_parts))
                intermediate_value = path_parts[1]
                match = re.search(r'\b\d+\b', intermediate_value)
                if match:
                    intermediate_value = match.group()

            else:
                print('ELSE_Len', len(path_parts))
                intermediate_value = path_parts[0]
                match = re.search(r'\b\d+\b', intermediate_value)
                if match:
                    intermediate_value = match.group()

            folder_name = os.path.basename(intermediate_value)
            print('intermediate_value', intermediate_value)
            local_subdirectory = os.path.join(local_directory, folder_name)
            print(f"Accessing folder: {folder}")
            try:
                # List all files in the folder
                files = sftp.listdir(folder)
                
                for file_name in files:
                    remote_file_path = f"{folder}/{file_name}"
                    local_file_path = os.path.join(local_subdirectory, file_name)

                    # Download each file
                    try:
                        print(f"Downloading {remote_file_path} to {local_file_path}")
                        sftp.get(remote_file_path, local_file_path)
                    except Exception as file_err:
                        print(f"Error downloading file {remote_file_path}: {file_err}")

            except FileNotFoundError:
                print(f"Folder not found on the server: {folder}")
                insert_detail_log(session, "Axis Finance Bank Reconciliation Process", "Axis Finance BRS Task", "N/A",
                            'BRS.AutoMail@axisfinance.in', f'N/A', f"Folder not found on the server: {folder}", loglevel="Failed")
            except Exception as folder_err:
                print(f"Error accessing folder {folder}: {folder_err}")

    except Exception as e:
        print(f"An error occurred: {e}")
        insert_detail_log(session, "Axis Finance Bank Reconciliation Process", "Axis Finance BRS Task", "N/A",
                            'BRS.AutoMail@axisfinance.in', f'N/A', f"An error occurred in SFTP: {e}", loglevel="Failed")
        insert_process_status(session, datetime.now(), "Axis Finance Bank Reconciliation Process",
                            "Axis Finance BRS Task", "N/A", 'BRS.AutoMail@axisfinance.in', "Failed", f"An error occurred in SFTP: {e}")

    finally:
        # Ensure connections are closed properly
        if sftp:
            try:
                sftp.close()
                print("SFTP connection closed.")
            except Exception as sftp_close_err:
                print(f"Error closing SFTP connection: {sftp_close_err}")
        if ssh:
            try:
                ssh.close()
                print("SSH connection closed.")
            except Exception as ssh_close_err:
                print(f"Error closing SSH connection: {ssh_close_err}")

    print("Script execution completed.")








#------------------------8350--------------------------
# •	AFL_GL_Interface_Staging_Data. File Type: - {Microsoft Excel Worksheet (.xlsx)}
# •	Bank Book 8350. File Type: - {Microsoft Excel Worksheet (.xlsx)}
# •	BRS- 8350. File Type: - {Microsoft Excel Worksheet (.xlsx)}
# •	TransactionSummary_918020079118350. File Type: - {Microsoft Excel 97-2003 Worksheet (.xls)}

#------------------------6033--------------------------
# •	AFL_GL_Interface_Staging_Data. File Type: - {Microsoft Excel Worksheet (.xlsx)}
# •	Bank Book 6033. File Type: - {Microsoft Excel Worksheet (.xlsx)}
# •	BRS- 6033. File Type: - {Microsoft Excel Worksheet (.xlsx)}
# •	TransactionSummary_918020079086033. File Type: - {Microsoft Excel 97-2003 Worksheet (.xls)}
# •	CASH AXIS FINANCE LTD MIS. File Type: - {Microsoft Excel 97-2003 Worksheet (.xls)}
# •	BBPS AXIS00000NATN6_MIS. File Type: - {Microsoft Excel Worksheet (.xlsx)}
# •	UPI UPI_Sett_AXIS FINANCE LIMITED. File Type: - {Microsoft Excel Comma Separated Values File (.csv)}

#------------------------607--------------------------
# •	AFL_GL_Interface_Staging_Data- I. File Type: - {Microsoft Excel Worksheet (.xlsx)}
# •	AFL_GL_Interface_Staging_Data- P. File Type: - {Microsoft Excel Worksheet (.xlsx)}
# •	Bank Book 607. File Type: - {Microsoft Excel Worksheet (.xlsx)}
# •	BRS- 607. File Type: - {Microsoft Excel Worksheet (.xlsx)}
# •	TransactionSummary_911020037637607. File Type: - {Microsoft Excel 97-2003 Worksheet (.xls)}

#------------------------669--------------------------
# •	AFL_GL_Interface_Staging_Data. File Type: - {Microsoft Excel Worksheet (.xlsx)}
# •	Bank Book 669. File Type: - {Microsoft Excel Worksheet (.xlsx)}
# •	BRS- 669. File Type: - {Microsoft Excel Worksheet (.xlsx)}
# •	TransactionSummary_918020103490669. File Type: - {Microsoft Excel 97-2003 Worksheet (.xls)}

#------------------------7687--------------------------
# •	BRS- 7687. File Type: - {Microsoft Excel Worksheet (.xlsx)}
# •	TransactionSummary_919020012447687. File Type: - {Microsoft Excel 97-2003 Worksheet (.xls)}

#------------------------9197--------------------------
# •	BRS- 9197. File Type: - {Microsoft Excel Worksheet (.xlsx)}
# •	TransactionSummary_919020036409197. File Type: - {Microsoft Excel 97-2003 Worksheet (.xls)}

