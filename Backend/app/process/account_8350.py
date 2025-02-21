import pandas as pd
from pathlib import Path
from app.init.config_loader import run as load_config
from app.config.constants import ConfigConstants
from app.db.db_engine import get_db_engine, get_session
from app.utils.custom_logger import general_logger, error_logger
from app.db.db_operations import insert_detail_log, insert_process_status
from app.utils.error_utils import handle_critical_error, file_not_found_error
from app.utils.dataframe_utils import check_columns
from app.init.email_service import start_mail,success_mail
from app.process import sftp_handler_axis
import os
import traceback
from datetime import datetime, timedelta
import openpyxl
import shutil
from app.utils.excel_styles import color_excel
from app.utils.load_utils import load_file
import re
import warnings
import sys
from app.process.upload_to_sftp_server import upload_file_sftp

warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)


# Initialize date variables
current_date = datetime.now()
valuedate = (current_date - timedelta(days=1)).strftime('%d-%m-%Y')
t_1_date = (current_date - timedelta(days=1)).strftime('%d.%m.%y')
t_2_date = (current_date - timedelta(days=2)).strftime('%d.%m.%y')
previousdate = (current_date - timedelta(days=1)).date()
t_1_date_bankbook = (current_date - timedelta(days=1)).strftime('%d-%m-%y')


# Initialize session and load configuration
session = get_session(get_db_engine())
config_data = load_config()
shared_folder = Path(ConfigConstants.INPUT_FOLDER)
# email_to = config_data['email_to']

output_folder = Path(ConfigConstants.OUTPUT_FOLDER)

def check_columns_exists(df, expected_columns, file_type, session, email_to, filepath):
    """Check for required columns in the DataFrame."""
    return check_columns(df, expected_columns, file_type, session, email_to, filepath)

def load_input_files(session, email_to, config_data):
    """Loads and validates input files."""
    dataframes = {}
    input_folder = Path(ConfigConstants.INPUT_FOLDER)
    transactionsummary_file = config_data['transactionsummary_8350']
    brs_file = config_data['brs_8350']
    afl_gl_interface_staging_data = config_data['AFL_GL_Interface_Staging_Data']
    bank_book_file = config_data['bank_book_8350']
    output_folder = Path(ConfigConstants.OUTPUT_FOLDER)
   
    try:
        # Load Transaction Summary file
        transactionsummary_filepath = input_folder / ConfigConstants.SUBFOLDER_8350 / transactionsummary_file
        general_logger.info(f"Loading Transaction Summary 8350 from {transactionsummary_filepath}")
        transactionsummary_df = load_file(transactionsummary_filepath, headerrow='Transaction Particulars', sheet_name='Sheet0')

        # Validate Transaction Summary columns
        if not check_columns_exists(transactionsummary_df, 
                                     ['Transaction Particulars', 'Value Date', 'Amount(INR)', 'DR|CR'], 
                                     'Transaction Summary 8350', session, email_to, transactionsummary_filepath):
            general_logger.error(f"Validation failed for Transaction Summary 8350 (File: {transactionsummary_filepath})")
            return None
        
        dataframes['Transaction Summary 8350'] = transactionsummary_df
        general_logger.info(f"Transaction Summary 8350 validated successfully (File: {transactionsummary_filepath})")

        # Load and validate BRS file
        brs_filepath = input_folder / ConfigConstants.SUBFOLDER_8350 / brs_file
        brs_output_folder = os.path.join(output_folder, ConfigConstants.SUBFOLDER_8350)
        shutil.copy(brs_filepath, brs_output_folder)
        general_logger.info(f"Loading BRS 8350 from {brs_filepath}")
        brs_8350_df = load_file(brs_filepath, headerrow='Date', sheet_name=t_2_date)

        if not check_columns_exists(brs_8350_df, 
                                     ['Particulars', 'Date', 'Amount'], 
                                     'BRS 8350', session, email_to, brs_filepath):
            general_logger.error(f"Validation failed for BRS 8350 (File: {brs_filepath})")
            return None
        
        dataframes['BRS 8350'] = brs_8350_df
        general_logger.info(f"BRS 8350 validated successfully (File: {brs_filepath})")

        # Load and validate Interface Staging file
        afl_gl_interface_staging_data_filepath = input_folder / ConfigConstants.SUBFOLDER_8350 / afl_gl_interface_staging_data
        general_logger.info(f"Loading AFL GL Interface Staging Data from {afl_gl_interface_staging_data_filepath}")
        afl_gl_interface_staging_data_df = load_file(afl_gl_interface_staging_data_filepath, headerrow='Accounting Code', sheet_name='AFL_GL_Interface_Staging_Data_1')

        if not check_columns_exists(afl_gl_interface_staging_data_df, 
                                     ['Accounting Code', 'Debit Amount', 'Credit Amount','Additional Field 1','Additional Field 2','Additional Field 3','Additional Field 4','Additional Field 5'], 
                                     'AFL GL Interface Staging Data', session, email_to, afl_gl_interface_staging_data_filepath):
            general_logger.error(f"Validation failed for AFL GL Interface Staging Data (File: {afl_gl_interface_staging_data_filepath})")
            return None
        
        dataframes['AFL_GL_Interface_Staging_Data'] = afl_gl_interface_staging_data_df
        general_logger.info(f"AFL GL Interface Staging Data validated successfully (File: {afl_gl_interface_staging_data_filepath})")

       


        # Load and validate bank book file
        bank_book_filepath = input_folder / ConfigConstants.SUBFOLDER_8350 / bank_book_file
        bank_book_8350_df = load_file(bank_book_filepath, headerrow='Date', sheet_name="Dec'24")

        if not check_columns_exists(bank_book_8350_df, 
                                     ['Particulars', 'Date'], 
                                     'Bank Book 8350', session, email_to, bank_book_filepath):
            general_logger.error(f"Validation failed for Bank book 8350 (File: {bank_book_filepath})")
            return None
        
        dataframes['Bank Book 8350'] = bank_book_8350_df
        general_logger.info(f"Bank Book 8350 validated successfully (File: {bank_book_filepath})")

        insert_detail_log(session, "Axis Finance Bank Reconciliation Process", "Axis Finance BRS Task", "N/A",
                            'BRS.AutoMail@axisfinance.in', f'N/A', f"Created Folder Structure of 8350", loglevel="Info")

        return dataframes

    except FileNotFoundError as e:
        e_type, e_obj, e_tb = sys.exc_info()
        print((str(e_tb.tb_lineno)))
        print('Exception Line Number - {0} , Exception Message - {1}'.format(str(e_tb.tb_lineno),e.__str__()))
        insert_detail_log(session, "Axis Finance Bank Reconciliation Process", "Axis Finance BRS Task", "N/A",
                            'BRS.AutoMail@axisfinance.in', f'{(str(e_tb.tb_lineno))}', f"{e.__str__()}", loglevel="Failed")
        insert_process_status(session, datetime.now(), "Axis Finance Bank Reconciliation Process",
                            "Axis Finance BRS Task", "N/A", 'BRS.AutoMail@axisfinance.in', "Failed", f"{e.__str__()}")
        error_logger.error(f"File not found: {e}")
        file_not_found_error(session, "File Loading", shared_folder, transactionsummary_file, email_to)
    except Exception as e:
        e_type, e_obj, e_tb = sys.exc_info()
        print((str(e_tb.tb_lineno)))
        print('Exception Line Number - {0} , Exception Message - {1}'.format(str(e_tb.tb_lineno),e.__str__()))
        insert_detail_log(session, "Axis Finance Bank Reconciliation Process", "Axis Finance BRS Task", "N/A",
                            'BRS.AutoMail@axisfinance.in', f'{(str(e_tb.tb_lineno))}', f"{e.__str__()}", loglevel="Failed")
        insert_process_status(session, datetime.now(), "Axis Finance Bank Reconciliation Process",
                            "Axis Finance BRS Task", "N/A", 'BRS.AutoMail@axisfinance.in', "Failed", f"{e.__str__()}")
        error_logger.error(f"Error while loading input files: {e}")
        traceback.print_exc()


# Function to check last three digits and update Remarks and Final Remark
def update_remarks(row):
    if isinstance(row['Transaction Particulars'], str) and row['Transaction Particulars'][-3:] == "607":
        row['Remarks'] = " Contra"
        row['Final Remarks'] = " Contra"
    return row

# Function to extract reference numbers or keep the original 'Flag' value if no match is found
def extract_reference(transaction, existing_flag):
    if isinstance(transaction, str) and any(txn in transaction for txn in ['NEFT', 'IFT', 'UTID', 'CB00']):
        match = re.search(r'/([^/]+)/', transaction)
        if match:
            return match.group(1)
    return existing_flag

def generate_transaction_report(transaction_df_df):
    """
    Generates a BRS (Bank Reconciliation Statement) report by filtering transactions
    on a specific 'Value Date' and performing various transformations, including 
    updating remarks and extracting flags. Saves the report to the specified output file.
    """
    filtered_df = transaction_df_df[transaction_df_df['Value Date'] == valuedate]
    closing_balance = filtered_df['Balance(INR)'].iloc[-1] if not filtered_df.empty else 0
    
    filtered_df['CHQNO']= filtered_df['CHQNO'].replace("-",None)
    filtered_df.loc[:, 'Flag'] = filtered_df['CHQNO'].str[-6:]
    filtered_df['Remarks'] = filtered_df['CHQNO'].apply(lambda x: 'CHQ' if pd.notnull(x) else '')
    filtered_df = filtered_df.apply(update_remarks, axis=1)
    filtered_df.loc[filtered_df['Transaction Particulars'].str.endswith("607-"), ['Remarks', 'Final Remarks']] = "Contra"

    filtered_df['Flag'] = filtered_df.apply(lambda row: extract_reference(row['Transaction Particulars'], row.get('Flag', '')), axis=1)
    # filtered_df['Working'] = filtered_df.apply(
    #     lambda row: ''.join(str(col) if pd.notnull(col) else '' for col in [int(row['Amount(INR)']), row['Flag']]), axis=1
    # )
    filtered_df['Amount(INR)']= pd.to_numeric(filtered_df['Amount(INR)'], errors = 'coerce')
    filtered_df['Amount(INR)']= filtered_df['Amount(INR)'].fillna(0).astype(int)
   
    filtered_df['Working'] = filtered_df.apply(
    lambda row: ''.join([
        str(row['Amount(INR)']) if pd.notnull(row['Amount(INR)']) else '',
        str(row['Flag']) if pd.notnull(row['Flag']) else ''
    ]), axis=1
    )
    
    # Extract contra data and add 'System' column
    contra_data = filtered_df[filtered_df['Remarks'].str.contains('Contra', na=False)].copy()
    contra_data['Remarks'] = 'Treasury'
    
    return filtered_df,closing_balance,contra_data

def generate_interface_report(afl_gl_interface_staging_data_df):
    """Filter the data for rows with an 'Accounting Code' of 221223 and 
    create a 'Working' column by concatenating 'Credit Amount' and 
    'Additional Field 5' as strings, ignoring null values.
    """
    filtered_df = afl_gl_interface_staging_data_df[afl_gl_interface_staging_data_df['Accounting Code'] == 221223]
    filtered_df['Credit Amount']= pd.to_numeric(filtered_df['Credit Amount'], errors = 'coerce')
    filtered_df['Credit Amount']= filtered_df['Credit Amount'].astype('Int64')
    filtered_df['Debit Amount']= pd.to_numeric(filtered_df['Debit Amount'], errors = 'coerce')
    filtered_df['Debit Amount']= filtered_df['Debit Amount'].astype("Int64")


    filtered_df['Working'] = filtered_df.apply(
        lambda row: ''.join(str(col) if pd.notnull(col) else '' for col in [row['Credit Amount'], row['Additional Field 5']]), axis=1
    )
    # Calculate subtotals for debit and credit amounts
    debit_subtotal = filtered_df['Debit Amount'].sum(skipna=True)
    credit_subtotal = filtered_df['Credit Amount'].sum(skipna=True)

    general_logger.info(
        f"Interface Report Generated: Debit Subtotal = {debit_subtotal}, Credit Subtotal = {credit_subtotal}"
    )
    
    return debit_subtotal, credit_subtotal,filtered_df

def generate_brs_report(brs_8350_df, brs_output_file):
    brs_8350_df['Working'] = brs_8350_df.apply(
        lambda row: ''.join(str(col) if pd.notnull(col) else '' for col in [row['Amount'], row['Cheque Number']]), axis=1)
    return brs_8350_df

def generate_bankbook_report(debit_subtotal, credit_subtotal, bank_book_df, contra_data):
    """
    Updates the Bank Book report by appending new transaction data, including receipt collections,
    reversals, and contra entries. Also formats the Date column and saves the updated report to a file.

    Args:
        debit_subtotal (float): Total debit amount to append.
        credit_subtotal (float): Total credit amount to append.
        bank_book_df (DataFrame): Original Bank Book DataFrame.
        contra_data (DataFrame): DataFrame containing contra transaction data.

    Returns:
        DataFrame: Updated Bank Book DataFrame.
    """
    try:
        # Prepare new data to append
        new_data = {
            'Date': [t_1_date_bankbook, t_1_date_bankbook],
            'Particulars': ['Receipt_Collection', 'Receipt_Reversal'],
            'Vch Type': ['Receipt', 'Payment'],
            'Debit': [debit_subtotal, ''],
            'Credit': ['', credit_subtotal],
            'Remarks': ['Indus', 'Indus']
        }

        # Create a DataFrame for new rows
        new_df = pd.DataFrame(new_data)

        # Process contra data
        contra_data = contra_data[['Value Date', 'Amount(INR)', 'Transaction Particulars', 'Remarks']].copy()
        contra_data.columns = ['Date', 'Debit', 'Particulars', 'Remarks']
        contra_data['Credit'] = ''  # Add a Debit column for consistency
        contra_data = contra_data[['Date', 'Particulars', 'Debit', 'Credit', 'Remarks']]  # Reorder columns
        contra_data['Vch Type'] = 'Contra'  # Assign voucher type as 'Contra'

        # Combine the original Bank Book, new data, and contra data
        bank_book_df = pd.concat([bank_book_df, new_df, contra_data], ignore_index=True)

        # Format the 'Date' column
        bank_book_df['Date'] = pd.to_datetime(bank_book_df['Date'], errors='coerce')
        # bank_book_df['Date'] = bank_book_df['Date'].dt.strftime('%d-%b-%y')
      

        bank_book_df['Net Balance'] = 0
        bank_book_df['Debit']= pd.to_numeric(bank_book_df['Debit'], errors = 'coerce')
        bank_book_df['Credit']= pd.to_numeric(bank_book_df['Credit'], errors = 'coerce')


        bank_book_df['Net Balance'] = bank_book_df['Net Balance'].loc[0]+(bank_book_df['Debit'].fillna(0) - bank_book_df['Credit'].fillna(0)).cumsum()
        book_balance = bank_book_df['Net Balance'].iloc[-1]

        # Save the updated Bank Book to an Excel file
        #bank_book_output_path = Path(output_folder)/'8350'/config_data['bank_book_8350']
        bank_book_output_path = os.path.join(output_folder, ConfigConstants.SUBFOLDER_8607,config_data['bank_book_8350'])

        bank_book_df.to_excel(bank_book_output_path, index=False)
        general_logger.info(f"Bank Book report saved successfully at {bank_book_output_path}")

        return book_balance

    except Exception as e:
        error_logger.error(f"Error in generating Bank Book report: {e}")
        traceback.print_exc()
        return bank_book_df  # Return original DataFrame in case of error


def match_and_reconcile(transaction_df, brs_df):
    # Filter Transaction Summary for rows with 'CHQ' in Remarks
    transaction_df_chq = transaction_df[transaction_df['Remarks'].str.contains('CHQ', na=False)]

    # Find matches and mismatches between BRS 'Working' and filtered Transaction Summary 'Working'
    matched_indices = transaction_df_chq[transaction_df_chq['Working'].isin(brs_df['Working'])].index
    mismatched_indices = transaction_df_chq[~transaction_df_chq['Working'].isin(brs_df['Working'])].index

    # Mark matched entries
    transaction_df.loc[matched_indices, 'Final Remarks'] = 'Clr from BRS'
    # Remove matched rows from BRS sheet
    brs_df = brs_df[~brs_df['Working'].isin(transaction_df_chq.loc[matched_indices, 'Working'])]

    # Mark mismatched entries
    transaction_df.loc[mismatched_indices, 'Final Remarks'] = 'Open'

    # Save the modified files
    # brs_df.to_excel(rf'{output_folder}\8350\Updated_BRS_Sheet.xlsx', index=False)
    # transaction_df.to_excel(rf'{output_folder}\8350\Updated_transaction_df.xlsx', index=False)

    return transaction_df, brs_df


def match_afl_to_transaction(transaction_df, afl_df, brs_df):
    """Match AFL data to Transaction Summary and update Remarks based on matching conditions."""
    
    try:
        # Convert 'Working' columns to a common format for accurate comparison if needed (e.g., strip whitespaces)
        afl_df['Working'] = afl_df['Working'].astype(str).str.strip()
        transaction_df['Working'] = transaction_df['Working'].astype(str).str.strip()

        # Perform the matching
        afl_df['Remarks'] = afl_df['Working'].apply(
            lambda x: 'Done in Bank Statement' if x in transaction_df['Working'].values else None)

        # transaction_df['Final Remarks'] = transaction_df['Working'].apply(
        #     lambda x: 'Done in indus file' if x in afl_df['Working'].values else 'Open')
        transaction_df['Final Remarks'] = transaction_df.apply(
            lambda row: 'Done in indus file' if row['Working'] in afl_df['Working'].values else row['Final Remarks'],axis=1)


        # transaction_df.to_excel(rf'{output_folder}\8350\Updated_transaction_df.xlsx', index=False)
        

        # # Fill blanks in 'Final Remarks' column in AFL data with 'Done in Bank Statement' if matched
        # afl_df['Final Remarks'] = afl_df['Final Remarks'].fillna(afl_df['Remarks'])
        # afl_df['Final Remarks'] = afl_df['Remarks']

        # Find matching entries in 'Working' column
        matching_entries = afl_df[(afl_df['Remarks'].isnull()) &(afl_df['Debit Amount'].notnull()) &
            (afl_df['Additional Field 4'].notnull())]

        # Create the 'Working' column by concatenating 'Debit Amount' and 'Additional Field 4'
        # matching_entries['Working'] = matching_entries['Debit Amount'].astype(str) + matching_entries['Additional Field 4'].astype(str)

        matching_entries['Working'] = matching_entries.apply(lambda row: ''.join(str(col) 
                if pd.notnull(col) else '' for col in [row['Debit Amount'], row['Additional Field 4']]), axis=1)

        # Filter matching entries between 'Working' columns of 'afl_df' and 'brs_data'
        matches = matching_entries[matching_entries['Working'].isin(brs_df['Working'])]

        # Update the 'Remarks' column in the original 'afl_df' DataFrame
        afl_df.loc[matches.index, 'Working'] = matching_entries['Working']
        afl_df.loc[matches.index, 'Remarks'] = 'Clr from BRS'
        afl_df['Final Remarks'] = afl_df['Remarks']


        # Remove matching rows from the BRS file
        brs_df = brs_df[~brs_df['Working'].isin(matches['Working'])]

        # Apply filters
        filtered_afl_df = afl_df[(afl_df['Final Remarks'].isnull()) & 
                                (afl_df['Additional Field 4'].isnull()) &(afl_df['Debit Amount'].notnull())]

        

        # Update the 'Remarks' column for filtered rows by adding 'Open'
        afl_df.loc[filtered_afl_df.index, 'Remarks'] = 'Open'

        # Apply filter for non-blank values in the 'Credit' column
        filtered_afl_df =  afl_df[(afl_df['Final Remarks'].isnull()) & 
                                (afl_df['Additional Field 4'].isnull()) & (afl_df['Credit Amount'].notnull())]

        # Update the 'Remarks' column for the filtered rows by adding 'Open'
        afl_df.loc[filtered_afl_df.index, 'Remarks'] = 'Open'


        # ++++++++++++++++++++++++++++++
        # Apply filter for rows where 'Final Remarks' column has 'Open'
        # transaction_df['Final Remarks'] = transaction_df['Final Remarks'].astype(str)
        # transaction_df['Final Remarks'] = transaction_df['Final Remarks'].apply(lambda x: str(x) if pd.notna(x) else '')
        # transaction_df['Final Remarks'] = transaction_df['Final Remarks'].fillna('').astype(str)

        # filtered_transaction_summary = transaction_df[transaction_df['Final Remarks'] == 'Open']
        filtered_transaction_summary = transaction_df[(transaction_df['Final Remarks'].isna())| (transaction_df['Final Remarks'] == 'Open')]


        # filtered_null = transaction_df[transaction_df['Final Remarks'].isna()| (transaction_df['Final Remarks']=="nan")]

        # # filtered_transaction_summary=pd.concat[filtered_transaction_summary,filtered_null]
        # filtered_transaction_summary = pd.concat([filtered_transaction_summary,filtered_null], ignore_index=True)


        # filtered_null.to_excel(rf'{output_folder}\8350\null.xlsx')
        # filtered_transaction_summary.to_excel(rf'{output_folder}\8350\open.xlsx')


        # # transaction_df['Final Remarks'] = transaction_df['Final Remarks'].fillna('').astype(str)
        # filtered_transaction_summary = transaction_df[transaction_df['Final Remarks'] == 'Open']

        
        # filtered_transaction_summary['Amount'] = filtered_transaction_summary.apply(
        #     lambda row: -row['Amount(INR)'] if row['DR|CR'].strip().upper() == 'DR' else row['Amount(INR)'], axis=1)
        filtered_transaction_summary['Amount'] = None
        filtered_transaction_summary['Final Remark'] = None
        if not filtered_transaction_summary.empty:
            filtered_transaction_summary['Amount'] = filtered_transaction_summary.apply(
            lambda row: -float(row['Amount(INR)']) if pd.notnull(row['Amount(INR)']) and 
                        row['DR|CR'].strip().upper() == 'DR' else row['Amount(INR)'], axis=1)

            # Final Remark based on Amount
            filtered_transaction_summary['Final Remark'] = filtered_transaction_summary.apply(
                lambda row: 'Debit in Bank Statement - Not in system' if row['DR|CR'].strip().upper() == 'DR' else 'Credit in Bank Statement - Not in system',
                axis=1)
        filtered_df = filtered_transaction_summary[['Value Date', 'Transaction Particulars', 'Amount','CHQNO', 'Final Remark']]
        filtered_df.columns = ['Date', 'Particulars', 'Amount','Loan No.', 'Final Remark']

        filtered_df['Additional Remarks'] = 'Pending from operation'


        afl_df['Remarks']= afl_df['Remarks'].apply(lambda x:"Open" if pd.isna(x) or x==""else x)
        filtered_afl_df = afl_df[afl_df['Remarks'] == 'Open']
        filtered_afl_df['Amount'] = filtered_afl_df.apply(
        lambda row: -row['Debit Amount'] if pd.notna(row['Debit Amount']) else row['Credit Amount'], axis=1)

        
       
      

        filtered_afl_df = filtered_afl_df[['Accounting Date', 'Additional Field 3', 'Amount', 'Additional Field 1', 'Additional Field 5']]
        filtered_afl_df.columns = ['Date', 'Particulars', 'Amount', 'Loan No.', 'Internal Remarks']

        filtered_afl_df['Final Remark'] = filtered_afl_df.apply(
            lambda row: 'Debit in system - Not in Bank Statement' if row['Amount'] < 0 else 'Credit in system - Not in Bank Statement', axis=1)

        brs_8350_df = pd.concat([brs_df,filtered_df,filtered_afl_df])

        brs_8350_df['Date'] = pd.to_datetime(brs_8350_df['Date'], format='%d-%m-%Y', errors='coerce', dayfirst=True)
        brs_8350_df['Aging'] = (pd.Timestamp(previousdate) - brs_8350_df['Date']).dt.days
        brs_8350_df['Aging Bucket'] = brs_8350_df['Aging'].apply(get_aging_bucket)
        brs_8350_df['Additional Remarks'] = 'Pending from operation'


    except Exception as e:
        e_type, e_obj, e_tb = sys.exc_info()
        print((str(e_tb.tb_lineno)))
        print('Exception Line Number - {0} , Exception Message - {1}'.format(str(e_tb.tb_lineno),e.__str__()))
        insert_detail_log(session, "Axis Finance Bank Reconciliation Process", "Axis Finance BRS Task", "N/A",
                            'BRS.AutoMail@axisfinance.in', f'{(str(e_tb.tb_lineno))}', f"{e.__str__()}", loglevel="Failed")
        insert_process_status(session, datetime.now(), "Axis Finance Bank Reconciliation Process",
                            "Axis Finance BRS Task", "N/A", 'BRS.AutoMail@axisfinance.in', "Failed", f"{e.__str__()}")


    return transaction_df, afl_df, brs_8350_df


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


def compute_final_summary(brs_8350_df, closing_balance,book_balance):
    """Compute the final summary for the report."""
    brs_8350_df['Amount'] = pd.to_numeric(brs_8350_df['Amount'], errors='coerce')

    total_value = (book_balance +
        get_total(brs_8350_df, 'Debit in Bank Statement - Not in system') +
        get_total(brs_8350_df, 'Credit in Bank Statement - Not in system') +
        get_total(brs_8350_df, 'Debit in system - Not in Bank Statement') +
        get_total(brs_8350_df, 'Credit in system - Not in Bank Statement')
    )
    summary_data = {
        'Description': ['Bank', 'A/C No.', 'Book Balance-BB', 'Debit in System - Not in Bank Statement', 
                        'Credit in System - Not in Bank Statement', 'Debit in Bank Statement - Not in system', 
                        'Credit in Bank Statement - Not in system', 'Balance as per Bank (Computed)', 
                        'Balance as per Bank Statement', 'Difference'],
        'Value': ['AXIS BANK – RETAIL DISBURSEMENT A/C -', '918020079118350', book_balance, 
                  get_total(brs_8350_df, 'Debit in system - Not in Bank Statement'),
                  get_total(brs_8350_df, 'Credit in system - Not in Bank Statement'),
                  get_total(brs_8350_df, 'Debit in Bank Statement - Not in system'),
                  get_total(brs_8350_df, 'Credit in Bank Statement - Not in system'),
                  
                  total_value , closing_balance, float(total_value) - float(closing_balance)]
    }
    return pd.DataFrame(summary_data)

def get_total(df, remark):
    """Calculate total for given remark condition."""
    return df[df['Final Remark'].str.contains(remark, na=False, case=False)]['Amount'].sum()

def save_report(brs_output_file, final_summary_df, brs_8350_df):
    """Save the final report to an Excel file."""
    general_logger.info(f"Saving final report to {brs_output_file}")
    with pd.ExcelWriter(brs_output_file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        pd.DataFrame({"Column1": ["Axis Finance Limited"]}).to_excel(writer, sheet_name=t_1_date, index=False, header=False, startrow=0,startcol=1)
        final_summary_df.to_excel(writer, sheet_name=t_1_date, index=False, startrow=1, startcol=1, header=False)
        brs_8350_df.to_excel(writer, sheet_name=t_1_date, index=False, startrow=len(final_summary_df) + 3)
    color_excel(brs_output_file, t_1_date)


def main_account_8350(to_email:str):
    """Main function that runs the BRS process for 8350."""
    try:
        start_mail(to_email,"Axis Finance BRS of Account 8350")


        try:
            sftp_handler_axis.sftp_hander(account_no = 8350)
        except Exception as e:
            print(f"Error occured in SFTP 8350")

        dataframes = load_input_files(session, to_email, config_data)
        if dataframes:
            transaction_df_df = dataframes['Transaction Summary 8350']
            brs_8350_df = dataframes['BRS 8350']
            afl_gl_interface_staging_data_df = dataframes['AFL_GL_Interface_Staging_Data']
            bank_book_df= dataframes['Bank Book 8350']
            output_folder = Path(ConfigConstants.OUTPUT_FOLDER)
            brs_output_file = os.path.join(output_folder, ConfigConstants.SUBFOLDER_8350, config_data['brs_8350'])
            
            transaction_df, closing_balance, contra_data=generate_transaction_report(transaction_df_df)

            brs_df=generate_brs_report(brs_8350_df, brs_output_file)
            general_logger.info("Generating Interface Report...")
            debit_subtotal, credit_subtotal, afl_df = generate_interface_report(afl_gl_interface_staging_data_df)
            book_balance= generate_bankbook_report(debit_subtotal, credit_subtotal, bank_book_df, contra_data)

            transaction_df, brs_df = match_and_reconcile(transaction_df, brs_df)

            transaction_df, afl_df, brs_8350_df = match_afl_to_transaction(transaction_df, afl_df,brs_df)
            final_summary_df = compute_final_summary(brs_8350_df, closing_balance, book_balance)

            insert_detail_log(session, "Axis Finance Bank Reconciliation Process", "Axis Finance BRS Task", "N/A",
                            'BRS.AutoMail@axisfinance.in', f'N/A', f"Working of Account 8350 is done", loglevel="Info")

            save_report(brs_output_file, final_summary_df, brs_8350_df)
            # match_afl_to_transaction(self, transaction_df, afl_df)
            general_logger.info("BRS process completed successfully.")
            
            #bank_book_output_path = Path(output_folder)/'8350'/config_data['bank_book_8350']
            bank_book_output_path = os.path.join(output_folder, ConfigConstants.SUBFOLDER_8607,config_data['bank_book_8350'])

            output_files =[brs_output_file,bank_book_output_path]
            upload_file_sftp((output_files), "8350")

            success_mail(to_email, "Axis Finance BRS",output_files)

            result = f""" Account 8350 have been processed successfully!!
            BRS Output File: {brs_output_file}
            Bank Book Output File: {bank_book_output_path}
            """
            status = "Success"
            return result, status
            
    except Exception as e:
        e_type, e_obj, e_tb = sys.exc_info()
        print((str(e_tb.tb_lineno)))
        print('Exception Line Number - {0} , Exception Message - {1}'.format(str(e_tb.tb_lineno),e.__str__()))
        insert_detail_log(session, "Axis Finance Bank Reconciliation Process", "Axis Finance BRS Task", "N/A",
                            'BRS.AutoMail@axisfinance.in', f'{(str(e_tb.tb_lineno))}', f"{e.__str__()}", loglevel="Failed")
        insert_process_status(session, datetime.now(), "Axis Finance Bank Reconciliation Process",
                            "Axis Finance BRS Task", "N/A", 'BRS.AutoMail@axisfinance.in', "Failed", f"{e.__str__()}")
        error_logger.error(f"Error in BRS process: {e}")
        handle_critical_error(session, "Axis bank", e, shared_folder, to_email)
        
        return f"Error in processing BRS for Account - 8350: {e}", "Failure"
