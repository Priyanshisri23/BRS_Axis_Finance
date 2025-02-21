import pandas as pd
import sys
from app.db.db_operations import insert_detail_log
from app.init.email_service import column_not_exist_mail
from app.utils.custom_logger import general_logger

def check_columns(df: pd.DataFrame, expected_columns: list, df_name: str, session, email_to, filepath):
    """
    Validates if the expected columns exist in the DataFrame.
    Logs the file path and actual columns in case columns are missing.
    """
    # Log actual columns from the dataframe for troubleshooting
    print(f"DF: {df}")
    actual_columns = df.columns.tolist()
    general_logger.info(f"Actual columns in {df_name} (File: {filepath}): {actual_columns}")

    # Find missing columns by comparing actual column names with expected ones
    missing_columns = [col for col in expected_columns if col not in actual_columns]

    if missing_columns:
        error_message = f"Missing columns in {df_name} (File: {filepath}): {missing_columns}"
        general_logger.error(error_message)
        column_not_exist_mail(df_name, missing_columns, email_to)
        insert_detail_log(session, "Missing columns", "Axis Finance Bank Reconciliation Statement", "N/A", email_to, "N/A",
                          f"Missing columns: {missing_columns} (File: {filepath})", "failed")
        # sys.exit(1)  # Exit the program if columns are missing

    general_logger.info(f"All required columns present in {df_name} (File: {filepath})")
    return True
