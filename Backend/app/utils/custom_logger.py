import logging
import os
from logging.handlers import RotatingFileHandler

import coloredlogs

from app.config.constants import ConfigConstants
from app.utils.custom_logger_bkp import logger


class CustomLogger:
    """Custom logger class that supports file and console logging with optional log rotation and colored logs."""

    def __init__(self, log_file_name, max_log_size=5 * 1024 * 1024, backup_count=5, enable_console=False):
        """
        Initializes the custom logger.

        :param log_file_name: The name of the log file (e.g., 'general_logs.txt' or 'error_logs.txt').
        :param max_log_size: The maximum size of the log file before rotation (in bytes).
        :param backup_count: The number of backup log files to keep.
        :param enable_console: Boolean to indicate if console logging should be enabled.
        """
        self.logger = logging.getLogger(log_file_name)
        self.logger.setLevel(logging.DEBUG)

        logs_path = ConfigConstants.LOGS_FOLDER
        os.makedirs(logs_path, exist_ok=True)

        # Create full log file path
        log_file_path = str(os.path.join(logs_path, log_file_name))

        # Check if handlers are already added to avoid duplicates
        if not self.logger.hasHandlers():
            # Create a rotating file handler
            file_handler = RotatingFileHandler(log_file_path, maxBytes=max_log_size, backupCount=backup_count)
            file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)

            # Add the file handler to the logger
            self.logger.addHandler(file_handler)

            # Optionally add console handler for debugging with colored logs
            if enable_console:
                coloredlogs.install(
                    logger=self.logger,
                    level='DEBUG',
                    fmt='%(asctime)s - %(levelname)s - %(message)s',  # Log format
                    datefmt='%Y-%m-%d %H:%M:%S',  # Date format
                    field_styles={
                        'asctime': {'color': 'green'},
                        'levelname': {'color': 'white', 'bold': True},
                        'message': {'color': 'blue'},
                    },
                    level_styles={
                        'debug': {'color': 'white'},
                        'info': {'color': 'blue'},
                        'warning': {'color': 'yellow'},
                        'error': {'color': 'red'},
                        'critical': {'color': 'red', 'bold': True, 'background': 'white'}
                    }
                )

    def get_logger(self):
        """Returns the logger instance."""
        return self.logger


# General Logger Instance with log rotation and optional console output
general_logger = CustomLogger('general_logs.log', enable_console=True).get_logger()

# Error Logger Instance with log rotation
error_logger = CustomLogger('error_logs.log').get_logger()

logger.info("Logger initialized")
