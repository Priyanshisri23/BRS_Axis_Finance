from app.utils.custom_logger import general_logger, error_logger
import pandas as pd
import os
from app.utils.error_utils import file_not_exist_email


def load_file(filepath, headerrow, sheet_name=None):
    """Helper function to load an Excel or CSV file based on its extension."""
    valid_extensions = ['.xlsx', '.xlsm', '.csv', '.CSV', '.xls']
    
    if filepath.suffix not in valid_extensions:
        raise ValueError(f"Unsupported file format: {filepath.suffix}. Expected one of {valid_extensions}.")
    
    general_logger.info(f"Loading file from {filepath} with header row ")

    if not filepath.exists():
        folder_name=os.path.dirname(filepath)
        file_name=os.path.basename(filepath)
        file_not_exist_email(file_name,folder_name)
        raise

    
    try:
        if filepath.suffix in ['.xlsx', '.xlsm', '.xls']:
            try:
                df = pd.read_excel(filepath, sheet_name=sheet_name)

            # except ValueError as e:
            #     # Log the error and fallback to the first sheet
            #     general_logger.error(f"Sheet named '{sheet_name}' not found in {filepath}. Loading the first available sheet.")
            #     df = pd.read_excel(filepath)  # Load the first sheet if specific one is missing
            except ValueError as e:
                # Log the error and fallback to the last available sheet
                general_logger.error(f"Sheet named '{sheet_name}' not found in {filepath}. Loading the last available sheet.")
                with pd.ExcelFile(filepath) as excelr:
                    last_sheet_name = excelr.sheet_names[-1]
                    df = pd.read_excel(excelr, sheet_name=last_sheet_name)
                    
        elif filepath.suffix in ['.csv', '.CSV']:
            df = pd.read_csv(filepath)

        # Find the row where the header is located
        # particulars_row = df[df.eq(headerrow).any(axis=1)].index[0]
        particulars_rows = df[df.eq(headerrow).any(axis=1)]

        print(particulars_rows)

        # Check if any rows were found
        if not particulars_rows.empty:
            particulars_row = particulars_rows.index[0]

            # Set the columns based on the row containing 'Particulars'
            df.columns = df.iloc[particulars_row]

            # Remove rows up to and including the 'Particulars' row, if needed
            df = df.iloc[particulars_row + 1:].reset_index(drop=True)
            df = df.dropna(subset=[headerrow])
            df.columns = df.columns.str.strip()
                       

        if df.empty:
            raise ValueError(f"File {filepath} is empty or could not be loaded properly.")
        
        general_logger.info(f"Successfully loaded file from {filepath}. Columns: {df.columns.tolist()}")
        return df
    except Exception as e:
        error_logger.error(f"Error loading file {filepath}: {str(e)}")
        # file_not_found_error(session, "File Loading", shared_folder, os.path.basename(filepath), email_to)
        #raise