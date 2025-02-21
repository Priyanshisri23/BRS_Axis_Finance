import paramiko
import os
import time
from dotenv import load_dotenv
from app.init.config_loader import run as load_config
from app.config.constants import ConfigConstants
from pathlib import Path
from app.db.db_engine import SessionLocal


config_data = load_config()

load_dotenv(ConfigConstants.ROOT_DIR_ENV + "/.env")
# session = get_session(get_db_engine())
session = SessionLocal
# hostname = os.getenv("FTP_HOST")
# port = os.getenv("FTP_PORT")
# username = os.getenv("SFTP_USERNAME")
# password = os.getenv("SFTP_PASSWORD")

# hostname = "10.9.129.47"
# port = 22  # Default SFTP port
# username = "SAP_Treasury"
# password = "Mumbai#2025"

def sftp_connection_decorator(hostname, port, username, password, max_retries=3, delay_between_retries=5):
    def decorator(func):
        """
        Uploads a file to the specified folder on an SFTP server with retry logic and error handling.

        :param hostname: SFTP server hostname or IP address.
        :param port: SFTP server port (default is 22).
        :param username: Username for authentication.
        :param password: Password for authentication.
        :param local_file_path: Path to the local file to be uploaded.
        :param remote_folder: Path to the remote folder where the file will be uploaded.
        :param max_retries: Maximum number of connection attempts (default is 3).
        :param delay_between_retries: Delay (in seconds) between connection attempts (default is 5).
        :return: None
        """
        def wrapper(*args, **kwargs):
            ssh = None
            sftp = None

            try:
                
                # Retry logic for connecting to the SFTP server
                max_retries = kwargs.get('max_retries', 3)
                delay_between_retries = kwargs.get('delay_between_retries', 5)

                for attempt in range(1, max_retries + 1):
                    try:
                        print(f"Attempt {attempt} to connect to the SFTP server...")
                        ssh = paramiko.SSHClient()
                        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        ssh.connect(hostname, port, username, password)
                        sftp = ssh.open_sftp()
                        return func(sftp, *args, **kwargs)
                        print("Connected to the SFTP server successfully.")
                        break
                    except Exception as conn_err:
                        print(f"Connection attempt {attempt} failed: {conn_err}")
                        if attempt < max_retries:
                            print(f"Retrying in {delay_between_retries} seconds...")
                            time.sleep(delay_between_retries)
                        else:
                            raise Exception("Failed to connect to the SFTP server after multiple attempts.")

            except Exception as e:
                print(f"An error occurred: {e}")

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

        return wrapper
    return decorator


@sftp_connection_decorator(
    hostname = os.getenv("FTP_HOST"),
    port = os.getenv("FTP_PORT"),  # Default SFTP port
    username = os.getenv("SFTP_USERNAME"),
    password = os.getenv("SFTP_PASSWORD")
)

# def upload_to_sftp(sftp, local_file_paths, remote_folder, **kwargs):

def upload_to_sftp(sftp, local_file_paths, remote_folder):

    # try:
    #     sftp.listdir(remote_folder)
    # except IOError:
    #     raise FileNotFoundError(f"Remote folder doest not exists: {remote_folder}")

    try:
        for local_file_path in local_file_paths:
            # Ensure the local file exists
            if not os.path.exists(local_file_path):
                print(f"Local file not found: {local_file_path}")

            # Construct remote file path
            remote_file_path = os.path.join(remote_folder, os.path.basename(local_file_path))
            remote_file_path = remote_file_path.replace("\\", "/")

            try:
                print(f"Uploading {local_file_path} to {remote_file_path} on the SFTP server...")
                sftp.put(local_file_path, remote_file_path)
                print(f"File uploaded successfully to {remote_file_path}.")
            except Exception as upload_err:
                raise Exception(f"Error uploading file to {remote_file_path}: {upload_err}")
    except Exception as e:
        print(f"An error occured during upload: {e}")
        raise



def upload_file_sftp(local_files, account):
    remote_folder= f"/BRS_UAT/Bank Reco {account}/Output Files"
    print("uprrRemoteeeeeeeeeeee",remote_folder)
   
    try:
        upload_to_sftp(local_files, remote_folder)

        #upload_to_sftp(local_files, remote_folder)
    except Exception as e:
        print(f"Error in Upload to SFTP: {e}")
        print("Remoteeeeeeeeeeee",remote_folder)