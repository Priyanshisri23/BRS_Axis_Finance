EMAIL_STYLES = {
    'font_family': 'Arial, sans-serif',
    'font_color': '#333',
    'background_color': '#F9F9F9',
    'footer_color': '#777777',
    'footer_background': '#F0F0F0',
    'container_padding': '20px',
    'header_padding': '10px',
    'content_margin_top': '20px',
    'footer_margin_top': '20px',

    # Specific Styles for Success Emails
    'success_header_background': '#2E7D32',  # Green
    'success_header_color': '#FFFFFF',

    # Specific Styles for Error Emails
    'error_header_background': '#D32F2F',  # Red
    'error_header_color': '#FFFFFF',

    # Specific Styles for Missing Column Emails
    'column_missing_header_background': '#F57C00',  # Orange
    'column_missing_header_color': '#FFFFFF',

    # Specific Styles for Missing File Emails
    'file_missing_header_background': '#C2185B',  # Pink
    'file_missing_header_color': '#FFFFFF',

    # Specific Styles for FTP Error Emails
    'ftp_error_header_background': '#FF6F61',  # Coral/Red for FTP Errors
    'ftp_error_header_color': '#FFFFFF',
}

PROCESS_NAME = "Axis Finance BRS"

# Subject templates
SUBJECT_STARTED_EXECUTION = f"[Process Initiated] - {PROCESS_NAME} Execution Has Begun"
SUBJECT_COMPLETED = f"[Success] - {PROCESS_NAME} Completed Successfully"
SUBJECT_ERROR = f"[Action Required] - Error Detected in {PROCESS_NAME}"
SUBJECT_FILE_MISSING = f"[Automation Halted] - Missing File for {PROCESS_NAME}"
SUBJECT_COLUMN_MISSING = f"[Automation Halted] - Invalid Column in {PROCESS_NAME}"
SUBJECT_SFTP_ERROR = f"[SFTP Error] - Failed to Access Files from FTP Server for {PROCESS_NAME}"
SUBJECT_BLANK_CAPS = f"[Automation FILE] - Output file in {PROCESS_NAME}"
SUBJECT_FTP_FILE_MISSING = f"[Automation Halted] - FTP File Missing in {PROCESS_NAME}"


# Body templates
BODY_STARTED_EXECUTION = (
    "Dear Team,\n\n"
    "This is an automated notification to inform you that the execution of the process <strong>{file_name}</strong> "
    "has been initiated as of <strong>{datetime}</strong>.\n\n"
    "The system will provide further updates as necessary.\n\n"
    "Regards,\n RPA Bot"
)

BODY_COMPLETED = (
    "Dear Team,\n\n"
    "This is an automated confirmation that the process <strong>{file_name}</strong> "
    "was successfully completed at <strong>{datetime}</strong>.\n\n"
    "No further action is required at this time.\n\n"
    "Regards,\n RPA Bot"
)

BODY_ERROR = (
    "Dear Team,\n\n"
    "An error was detected in the execution of the process <strong>{file_name}</strong> at <strong>{datetime}</strong>.\n\n"
    "Error Details:\n"
    "- <strong>Error Message:</strong> {error_message}\n"
    "- <strong>Line Number:</strong> {line_number}\n\n"
    "Further investigation is recommended to resolve the issue.\n\n"
    "Regards,\n RPA Bot"
)

BODY_FILE_MISSING = (
    "Dear Team,\n\n"
    "Automation for <strong>{file_name}</strong> has been halted due to a missing input file in the folder "
    "'<strong>{folder_name}</strong>'.\n\n"
    "Please add the required file to the folder and restart the process to continue execution.\n\n"
    "Regards,\n RPA Bot"
)

BODY_COLUMN_MISSING = (
    "Dear Team,\n\n"
    "Automation for the process <strong>{file_name}</strong> was stopped due to an invalid column detected in the file.\n\n"
    "Affected Column(s): <strong>{column_name}</strong>\n"
    "Detection Time: <strong>{datetime}</strong>\n\n"
    "Please correct the file structure and restart the automation.\n\n"
    "Regards,\n RPA Bot"
)

BODY_FTP_ERROR = (
    "Hello Team,\n\n"
    "An issue was encountered while attempting to access files from the FTP server for process <strong>{file_name}</strong>.\n\n"
    "Error Message: <strong>{error_message}</strong>\n"
    "This error was detected on <strong>{datetime}</strong>.\n\n"
    "Please investigate the issue and ensure that the FTP server is accessible and the files are available.\n\n"
    "Thanks and Regards,\n RPA"
)