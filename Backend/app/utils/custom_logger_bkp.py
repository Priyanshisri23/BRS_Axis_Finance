import logging
import os

# Define the log file path
LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../backend.log')

# Create a custom logger
logger = logging.getLogger('custom_logger')
logger.setLevel(logging.DEBUG)  # Set the logging level

# Create handlers
file_handler = logging.FileHandler(LOG_FILE_PATH)
file_handler.setLevel(logging.DEBUG)

# Create formatters and add them to handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)

