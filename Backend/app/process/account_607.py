import pandas as pd
from pathlib import Path
from app.init.config_loader import run as load_config
from app.config.constants import ConfigConstants
from app.db.db_engine import get_db_engine, get_session
from app.utils.custom_logger import general_logger, error_logger
from app.db.db_operations import insert_detail_log, insert_process_status
from app.utils.error_utils import handle_critical_error, file_not_found_error
from app.utils.dataframe_utils import check_columns
import os
import traceback
from datetime import datetime, timedelta
import shutil
from app.utils.excel_styles import color_excel
from app.utils.load_utils import load_file
from app.process import sftp_handler_axis
import re
import warnings
from app.init.email_service import start_mail, success_mail
from app.process.upload_to_sftp_server import upload_file_sftp

warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)



# Initialize date variables
current_date = datetime.now()
valuedate = (current_date - timedelta(days=1)).strftime('%d-%m-%Y')
trans_date = (current_date - timedelta(days=1)).strftime('%d-%b-%y')
t_1_date = (current_date - timedelta(days=1)).strftime('%d.%m.%y')
t_1_date_bankbook = (current_date - timedelta(days=1)).strftime('%d-%m-%y')

t_2_date = (current_date - timedelta(days=2)).strftime('%d.%m.%y')
previousdate = (current_date - timedelta(days=1)).date()

# Initialize session and load configuration
session = get_session()
config_data = load_config()
shared_folder = Path(ConfigConstants.INPUT_FOLDER)
# email_to = config_data['email_to']

# email_to 
output_folder = Path(ConfigConstants.OUTPUT_FOLDER)

def check_columns_exists(df, expected_columns, file_type, session, email_to, filepath):
    """Check for required columns in the DataFrame."""
    return check_columns(df, expected_columns, file_type, session, email_to, filepath)

def load_and_validate_file(filepath, headerrow, sheet_name, required_columns, dataframe_key, session, email_to, dataframes):
    """
    Helper function to load a file and validate its columns.
    :param filepath: Path to the file to be loaded.
    :param headerrow: Row to be used as the header.
    :param sheet_name: The sheet to be loaded from the Excel file.
    :param required_columns: List of required column names to validate.
    :param dataframe_key: Key for storing the DataFrame in the dictionary.
    :param session: Session for logging and error handling.
    :param email_to: Email recipient for error notifications.
    :param dataframes: Dictionary to store the loaded DataFrame.
    :return: Boolean indicating success or failure of file loading and validation.
    """
    try:
        general_logger.info(f"Loading {dataframe_key} from {filepath}")
        df = load_file(filepath, headerrow=headerrow, sheet_name=sheet_name)
        
        # Validate columns
        if not check_columns_exists(df, required_columns, dataframe_key, session, email_to, filepath):
            general_logger.error(f"Validation failed for {dataframe_key} (File: {filepath})")
            return False
        
        dataframes[dataframe_key] = df
        general_logger.info(f"{dataframe_key} validated successfully (File: {filepath})")
        return True

    except Exception as e:
        general_logger.error(f"Error while loading and validating {dataframe_key} (File: {filepath}): {e}")
        traceback.print_exc()
        return False


def load_input_files(session, email_to, config_data):
    """Loads and validates input files."""
    dataframes = {}
    input_folder = Path(ConfigConstants.INPUT_FOLDER)
    output_folder = Path(ConfigConstants.OUTPUT_FOLDER)
    sub_output_folder = os.path.join(output_folder, ConfigConstants.SUBFOLDER_8607)
    subfolder = Path(ConfigConstants.SUBFOLDER_8607)

    print(f"Subfolder path: {subfolder}, Input folder: {input_folder}")
    transactionsummary_file = config_data['transactionsummary_8607']
    brs_file = config_data['brs_8607']
    bank_book_file = config_data['bank_book_8607']
    afl_gl_interface_staging_data = config_data['AFL_GL_Interface_Staging_Data_Indus']
    afl_gl_interface_staging_pennant = config_data['AFL_GL_Interface_Staging_Pennant']

    try:
        # Load and validate Transaction Summary file
        transactionsummary_filepath = input_folder / subfolder / transactionsummary_file
        print("Transaction file path", transactionsummary_filepath)
        if not load_and_validate_file(transactionsummary_filepath, 
                                      'Transaction Particulars', 'Sheet0', 
                                      ['Transaction Particulars', 'Value Date', 'Amount(INR)', 'DR|CR'], 
                                      'Transaction Summary 8607', session, email_to, dataframes):
            return None
        
        # Load and validate Bank Book file
        bank_book_filepath = input_folder / subfolder / bank_book_file
        if not load_and_validate_file(bank_book_filepath, 
                                      'Particulars', "Dec'24", 
                                      ['Particulars', 'Date'], 
                                      'BANK_BOOK_607', session, email_to, dataframes):
            return None
        
        # Load and validate AFL GL Interface Staging Data file
        afl_gl_interface_staging_data_filepath = input_folder / subfolder / afl_gl_interface_staging_data
        if not load_and_validate_file(afl_gl_interface_staging_data_filepath, 
                                      'Accounting Code', 'AFL_GL_Interface_Staging_Data_1', 
                                      ['Accounting Code', 'Debit Amount', 'Credit Amount', 
                                       'Additional Field 1', 'Additional Field 2', 'Additional Field 3', 
                                       'Additional Field 4', 'Additional Field 5'], 
                                      'AFL_GL_Interface_Staging_Data', session, email_to, dataframes):
            return None

        # Load and validate AFL GL Interface Staging Pennant file
        afl_gl_interface_staging_pennant_filepath = input_folder / subfolder / afl_gl_interface_staging_pennant
        if not load_and_validate_file(afl_gl_interface_staging_pennant_filepath, 
                                      'Accounting Code', 'AFL_GL_Interface_Staging_Data_1', 
                                      ['Accounting Code', 'Debit Amount', 'Credit Amount', 
                                       'Additional Field 1', 'Additional Field 2', 'Additional Field 3', 
                                       'Additional Field 4', 'Additional Field 5'], 
                                      'AFL_GL_Interface_Staging_Pennant', session, email_to, dataframes):
            return None
        
        # Load BRS file
        brs_filepath = input_folder / subfolder / brs_file
        shutil.copy(brs_filepath, sub_output_folder)
        if not load_and_validate_file(brs_filepath, 
                                      'Date', t_2_date, 
                                      ['Particulars', 'Date', 'Amount'], 
                                      'BRS 8607', session, email_to, dataframes):
            return None
        return dataframes

    except FileNotFoundError as e:
        error_logger.error(f"File not found: {e}")
    except Exception as e:
        error_logger.error(f"Error while loading input files: {e}")
        traceback.print_exc()




def generate_transaction_report(transaction_df):
    """
    Generates a BRS (Bank Reconciliation Statement) report by filtering transactions
    based on a specific 'Value Date' and performing transformations such as updating remarks
    and extracting flags. Returns filtered data and contra data.

    Args:
    transaction_df (pd.DataFrame): The DataFrame containing transaction data.
    
    Returns:
    filtered_df (pd.DataFrame): The filtered DataFrame with remarks updated.
    closing_balance (float): The closing balance based on the filtered transactions.
    contra_data (pd.DataFrame): The extracted contra data with 'Credit', 'Debit', and 'System' columns.
    """
    # Filter transactions based on 'Value Date'
    filtered_df = transaction_df[transaction_df['Value Date'] == valuedate]
    
    # Return early if no matching data is found
    if filtered_df.empty:
        return filtered_df, 0, pd.DataFrame()

    # Calculate closing balance (last balance if the DataFrame is not empty)
    closing_balance = filtered_df['Balance(INR)'].iloc[-1] if not filtered_df.empty else 0

    filtered_df['Amount(INR)']= pd.to_numeric(filtered_df['Amount(INR)'], errors = 'coerce')
    filtered_df['Remarks'] = ''
    identifiers = ['607-', '6033-','8524-']
    
    # Apply 'Contra' remark where transaction details match identifiers
    mask = filtered_df['Transaction Particulars'].str.contains('|'.join(identifiers), na=False)
    filtered_df.loc[mask, 'Remarks'] = 'Contra'

    # Extract Contra data where 'Remarks' contains 'Contra'
    contra_data = filtered_df[filtered_df['Remarks'] == 'Contra'].copy()
    # Add 'Credit' and 'Debit' columns based on 'DR|CR' column
    contra_data["Credit"] = contra_data["Amount(INR)"].where(contra_data["DR|CR"] == "DR", 0)
    contra_data["Debit"] = contra_data["Amount(INR)"].where(contra_data["DR|CR"] == "CR", 0)
    contra_data["Vch Type"] = 'Contra'

    # Add 'System' column with a constant value
    contra_data['System'] = 'Treasury'

    # print("yecheck l",contra_data.columns)
    filtered_df['Amount'] = filtered_df.apply(
        lambda row: -row['Amount(INR)'] if row['DR|CR'].strip().upper() == 'DR' else row['Amount(INR)'], axis=1)
    
    filtered_df['Final Remark'] = filtered_df.apply(
        lambda row: 'Debit in Bank Statement - Not in system' if float(row['Amount']) < 0 else 'Credit in Bank Statement - Not in system', axis=1) 
    
    filtered_df = filtered_df[~filtered_df['Remarks'].str.contains('Contra', na=False)].copy()

    transaction_data = filtered_df[['Value Date', 'Transaction Particulars', 'Amount','Final Remark']]
    transaction_data.columns = ['Date', 'Particulars', 'Amount','Final Remark']

    return transaction_data, closing_balance, contra_data


def generate_interface_report_indus(afl_gl_interface_staging_data_df):
    """
    Filters data for rows with an 'Accounting Code' of 221211, computes subtotals 
    for debit and credit amounts.
    
    Args:
        afl_gl_interface_staging_data_df (pd.DataFrame): Input DataFrame with GL interface data.

    Returns:
        tuple: A tuple containing:
            - debit_subtotal (float): Sum of 'Debit Amount'.
            - credit_subtotal (float): Sum of 'Credit Amount'.
    """
    try:
        # Filter rows where 'Accounting Code' equals 221211
        afl_filtered_df = afl_gl_interface_staging_data_df[afl_gl_interface_staging_data_df['Accounting Code'] == 221211].copy()

        # Early return if no data is found
        if afl_filtered_df.empty:
            general_logger.warning("No rows found with 'Accounting Code' = 221211.")
            return 0, 0

        # Calculate subtotals for debit and credit amounts
        debit_subtotal = afl_filtered_df['Debit Amount'].sum()
        credit_subtotal = afl_filtered_df['Credit Amount'].sum()

        # Log the results
        general_logger.info(f"Interface Report Generated: Debit Subtotal = {debit_subtotal}, Credit Subtotal = {credit_subtotal}")

        return debit_subtotal, credit_subtotal

    except Exception as e:
        # Log the error details
        error_logger.error(f"Error generating interface report: {e}")
        traceback.print_exc()  # Print the full traceback for debugging
        return 0, 0, pd.DataFrame()  # Return empty DataFrame on error



def generate_interface_report_pennant(afl_gl_interface_staging_pennant_df):
    """
    Filters data for rows with an 'Accounting Code' of 221211, computes subtotals 
    for debit and credit amounts, and creates a 'Working1' column with concatenated 
    information from 'Debit Amount' or 'Credit Amount' and 'Additional Field 2'.
    
    Args:
        afl_gl_interface_staging_pennant_df (pd.DataFrame): Input DataFrame with GL interface data.
        bank_book_df (pd.DataFrame): Existing Bank Book DataFrame to update with new data.

    Returns:
        tuple: A tuple containing:
            - afl_filtered_df (pd.DataFrame): Filtered and transformed DataFrame.
            - bank_book_df (pd.DataFrame): Updated Bank Book DataFrame.
    """
    try:
        # Filter rows where 'Record Status' is either NaN or empty string
        afl_gl_interface_staging_pennant_df['Transaction Date'] = pd.to_datetime(afl_gl_interface_staging_pennant_df['Transaction Date'],format='%d-%m-%y', errors='coerce')        
        print('---->', afl_gl_interface_staging_pennant_df)
        filtered_df = afl_gl_interface_staging_pennant_df[afl_gl_interface_staging_pennant_df['Transaction Date'] == trans_date]
        print('---->FILTER', filtered_df)

        # Filter rows where 'Accounting Code' equals 221211
        afl_filtered_df = filtered_df[filtered_df['Accounting Code'] == 221211].copy()

        # afl_filtered_df['Amount'] = afl_filtered_df.apply(lambda row: -row['Debit Amount'] if pd.notna(row['Debit Amount']) else row['Credit Amount'], axis=1)

        afl_filtered_df['Amount'] = afl_filtered_df.apply(lambda row: -row['Debit Amount'] if (row['Debit Amount'] > 0) else row['Credit Amount'], axis=1)


        afl_brs_df = afl_filtered_df[['Transaction Date', 'Additional Field 3', 'Amount', 'Additional Field 5']]
        afl_brs_df.columns = ['Date', 'Particulars', 'Amount', 'Internal Remarks']

        # Prepare AFL dataframe for concatenation
        afl_bankbook_df = afl_filtered_df[['Transaction Date', 'Additional Field 3', 'Debit Amount', 'Credit Amount', 'Additional Field 5']]
        afl_bankbook_df.columns = ['Date', 'Particulars','Debit' , 'Credit', 'Reference Number']

        if afl_filtered_df.empty:
            general_logger.warning("No rows found with 'Accounting Code' = 221211 or matching 'Record Status'.")
            return afl_bankbook_df, afl_brs_df      

        # Add 'Vch Type' column based on 'Debit' and 'Credit' values
        afl_bankbook_df['Vch Type'] = afl_bankbook_df.apply(
            lambda row: 'Receipt' if row['Debit'] > 0 else 'Payment' if row['Credit'] > 0 else None,axis=1)


        afl_brs_df['Final Remark'] = afl_brs_df.apply(
        lambda row: 'Debit in system - Not in Bank Statement' if row['Amount'] < 0 else 'Credit in system - Not in Bank Statement', axis=1)



        # Log transformation results
        general_logger.info(f"Filtered and transformed {len(afl_filtered_df)} rows for AFL interface data.")

        return afl_bankbook_df, afl_brs_df  

    except Exception as e:
        # Log the error details
        error_logger.error(f"Error generating interface report for Pennant: {e}")
        traceback.print_exc()
        return pd.DataFrame(),pd.DataFrame()



def generate_bankbook_report(bank_book_df, contra_data,debit_subtotal,credit_subtotal,afl_bankbook_pennat_df,bank_book_output_file):
    """
    Updates the Bank Book report by appending new transaction data, including receipt collections,
    reversals, and contra entries. Also formats the Date column and saves the updated report to a file.

    Args:
        bank_book_df (pd.DataFrame): Original Bank Book DataFrame.
        contra_data (pd.DataFrame): DataFrame containing contra transaction data.
        output_folder (str): Path to the folder where the updated bank book will be saved.

    Returns:
        pd.DataFrame: Updated Bank Book DataFrame.
    """
    try:

        # Prepare new data to append
        new_data = {
            'Date': [t_1_date_bankbook, t_1_date_bankbook],
            'Particulars': ['Receipt_Collection', 'Receipt_Reversal'],
            'Vch Type': ['Receipt', 'Payment'],
            'Debit': [debit_subtotal, ''],
            'Credit': ['', credit_subtotal],
            'System': ['Indus', 'Indus']
        }

        # Create a DataFrame for new rows
        new_df = pd.DataFrame(new_data)
        # Process contra data by renaming columns to match Bank Book structure
       
        contra_data = contra_data[['Value Date', 'Credit', 'Debit', 'Vch Type', 'Transaction Particulars', 'System']].copy()
        print("Process contra data by renaming column",contra_data.column)
        contra_data.columns = ['Date', 'Credit', 'Debit', 'Vch Type', 'Particulars', 'System']

        # Combine the original Bank Book, new data, and contra data
        bank_book_df = pd.concat([bank_book_df, new_df, contra_data,afl_bankbook_pennat_df], ignore_index=True)

        bank_book_df['Date'] = pd.to_datetime(bank_book_df['Date'], errors='coerce', dayfirst=True)

        bank_book_df['Net Balance'] = 0
        bank_book_df['Debit']= pd.to_numeric(bank_book_df['Debit'], errors = 'coerce')
        bank_book_df['Credit']= pd.to_numeric(bank_book_df['Credit'], errors = 'coerce')


        bank_book_df['Net Balance'] =bank_book_df['Net Balance'].iloc[0]+(bank_book_df['Debit'].fillna(0) - bank_book_df['Credit'].fillna(0)).cumsum()
        book_balance = bank_book_df['Net Balance'].iloc[-1]

        bank_book_df.to_excel(bank_book_output_file, index=False)

        return book_balance

    except Exception as e:
        error_logger.error(f"Error in generating Bank Book report: {e}")
        traceback.print_exc()
        return bank_book_df


def generate_brs_report(transaction_summary_df, brs_df, afl_brs_pennat_df):
    try:
        """Generate and save the BRS report."""
        brs_df = pd.concat([brs_df, transaction_summary_df,afl_brs_pennat_df], ignore_index=True)
        brs_df['Date'] = pd.to_datetime(brs_df['Date'], format='%d-%m-%Y', errors='coerce', dayfirst=True)
        brs_df['Aging'] = (pd.Timestamp(previousdate) - brs_df['Date']).dt.days
        brs_df['Aging Bucket'] = brs_df['Aging'].apply(get_aging_bucket)
        brs_df['Additional Remarks'] = 'Pending from operation'

        return brs_df

    except Exception as e:
        error_logger.error(f"Error in generating Bank Book report: {e}")
        traceback.print_exc()
        return brs_df

    



def get_aging_bucket(aging_days):
    """Categorize aging days into buckets."""
    if aging_days < 0:
        return 'Future Date'
    elif aging_days <= 30:
        return '0 to 30 days'
    elif aging_days <= 60:
        return '30 to 60 days'
    elif aging_days <= 90:
        return '60 to 90 days'
    return '90 days & above'


def compute_final_summary(brs_8607_df, closing_balance, book_balance ):
    """Compute the final summary for the report."""

   
    brs_8607_df['Amount'] = pd.to_numeric(brs_8607_df['Amount'], errors='coerce')

    # print(book_balance)
    # print(get_total(brs_8607_df, 'Debit in Bank Statement - Not in system'))
    # print(get_total(brs_8607_df, 'Credit in Bank Statement - Not in system'),get_total(brs_8607_df, 'Debit in system - Not in Bank Statement'),
    #     get_total(brs_8607_df, 'Credit in system - Not in Bank Statement'))

    total_value = (book_balance +
        get_total(brs_8607_df, 'Debit in Bank Statement - Not in system') +
        get_total(brs_8607_df, 'Credit in Bank Statement - Not in system') +
        get_total(brs_8607_df, 'Debit in system - Not in Bank Statement') +
        get_total(brs_8607_df, 'Credit in system - Not in Bank Statement')
    )


    summary_data = {
        'Description': ['Bank', 'A/C No.', 'Book Balance-BB', 'Debit in System - Not in Bank Statement', 
                        'Credit in System - Not in Bank Statement', 'Debit in Bank Statement - Not in system', 
                        'Credit in Bank Statement - Not in system', 'Balance as per Bank (Computed)', 
                        'Balance as per Bank Statement', 'Difference'],
        'Value': ['AXIS BANK – RETAIL COLLECTION A/C ', '91802007908607', book_balance , 
                  get_total(brs_8607_df, 'Debit in system - Not in Bank Statement'),
                  get_total(brs_8607_df, 'Credit in system - Not in Bank Statement'),
                  get_total(brs_8607_df, 'Debit in Bank Statement - Not in system'),
                  get_total(brs_8607_df, 'Credit in Bank Statement - Not in system'),
                  total_value , closing_balance, float(total_value) - float(closing_balance)]
    }
    return pd.DataFrame(summary_data)

def get_total(df, remark):
    """Calculate total for given remark condition."""
    return df[df['Final Remark'].str.contains(remark, na=False, case=False)]['Amount'].sum()

def save_report(brs_output_file, final_summary_df, brs_8607_df):
    """Save the final report to an Excel file."""
    general_logger.info(f"Saving final report to {brs_output_file}")
    with pd.ExcelWriter(brs_output_file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        pd.DataFrame({"Column1": ["Axis Finance Limited"]}).to_excel(writer, sheet_name=t_1_date, index=False, header=False, startrow=0,startcol=1)
        final_summary_df.to_excel(writer, sheet_name=t_1_date, index=False, startrow=1, startcol=1, header=False)
        brs_8607_df.to_excel(writer, sheet_name=t_1_date, index=False, startrow=len(final_summary_df) + 3)
    color_excel(brs_output_file, t_1_date)



def main_account_607(to_email:str):
    """Main function that runs the BRS process for 8607."""
    try:
        start_mail(to_email,"Axis Finance BRS of Account 607")


        try:
            sftp_handler_axis.sftp_hander(account_no = 607)
        except Exception as e:
            print(f"Error occured in SFTP 607")

        # Load input files and handle case where files might not be loaded properly
        dataframes = load_input_files(session, to_email, config_data)
        
        if not dataframes:
            raise ValueError("Error loading input dataframes.")
        
        # Destructure the dataframes for easier reference
        transaction_df = dataframes.get('Transaction Summary 8607')
        bank_book_df = dataframes.get('BANK_BOOK_607')
        brs_8607_df = dataframes.get('BRS 8607')
        afl_gl_interface_staging_data_df = dataframes.get('AFL_GL_Interface_Staging_Data')
        afl_gl_interface_staging_pennant_df = dataframes.get('AFL_GL_Interface_Staging_Pennant')
        
        # Check if required dataframes exist
        required_dataframes = [
            transaction_df, bank_book_df, brs_8607_df, 
            afl_gl_interface_staging_data_df, afl_gl_interface_staging_pennant_df]
        if any(df is None for df in required_dataframes):
            raise ValueError("One or more required dataframes are missing.")
        
        # Define output folder and file path
        output_folder = Path(ConfigConstants.OUTPUT_FOLDER)
        brs_output_file = os.path.join(output_folder, ConfigConstants.SUBFOLDER_8607, config_data['brs_8607'])
        bank_book_output_file = os.path.join(output_folder, ConfigConstants.SUBFOLDER_8607, config_data['bank_book_8607'])


        # Generate transaction report
        transaction_df, closing_balance, contra_data = generate_transaction_report(transaction_df)
        debit_subtotal,credit_subtotal = generate_interface_report_indus(afl_gl_interface_staging_data_df)
        # Generate AFL GL interface reports
        afl_df_bankbook, afl_df_brs = generate_interface_report_pennant(afl_gl_interface_staging_pennant_df)
        book_balance = generate_bankbook_report(bank_book_df, contra_data,debit_subtotal,credit_subtotal,afl_df_bankbook,bank_book_output_file)
        brs_8607_df = generate_brs_report(transaction_df, brs_8607_df, afl_df_brs)
        # Compute final summary of the report
        final_summary_df = compute_final_summary(brs_8607_df, closing_balance, book_balance)
        # Save the report
        save_report(brs_output_file, final_summary_df, brs_8607_df)

        upload_file_sftp(([brs_output_file, bank_book_output_file]), "607")
        success_mail(to_email,"Axis Finance BRS",[brs_output_file, bank_book_output_file])

        result = f""" Account 607 have been processed successfully!!
        BRS Output File: {brs_output_file}
        Bank Book Output File: {bank_book_output_file}
        """
        status = "Success"
        return result, status
    
    except Exception as e:
        # Error handling with specific details for troubleshooting
        error_logger.error(f"Error in BRS process: {e}")
        traceback.print_exc()
        
        # Ensure critical error handling and notifications
        handle_critical_error(session, "Axis bank", e, shared_folder, to_email)

        return f"Error in processing BRS for Account - 607: {e}", "Failure"