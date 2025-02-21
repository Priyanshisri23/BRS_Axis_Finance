import pysftp
import os

SFTP_HOST = "s2fs.axisbank.com"
SFTP_USERNAME = "SAP_Treasury"
SFTP_PASSWORD = "Mumbai#2025"

class SFTPClient:
    def __init__(self):
        self.host = SFTP_HOST
        self.username = SFTP_USERNAME
        self.password = SFTP_PASSWORD

    def list_files(self, remote_path: str = "."):
        """List files in a remote directory."""
        with pysftp.Connection(self.host, username=self.username, password=self.password) as sftp:
            sftp.cwd(remote_path)
            return sftp.listdir()

    def download_file(self, remote_path: str, local_path: str):
        """Download a file from the SFTP server."""
        with pysftp.Connection(self.host, username=self.username, password=self.password) as sftp:
            sftp.get(remote_path, local_path)
            return f"File downloaded to {local_path}"

    def upload_file(self, local_path: str, remote_path: str):
        """Upload a file to the SFTP server."""
        with pysftp.Connection(self.host, username=self.username, password=self.password) as sftp:
            sftp.put(local_path, remote_path)
            return f"File uploaded to {remote_path}"
