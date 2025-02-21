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
print(current_date)
valuedate = (current_date - timedelta(days=1)).strftime('%d-%m-%Y')
t_1_date = (current_date - timedelta(days=1)).strftime('%d.%m.%Y')
t_1_date_bankbook = (current_date - timedelta(days=1)).strftime('%d-%m-%y')

t_2_date = (current_date - timedelta(days=2)).strftime('%d.%m.%y')
previousdate = (current_date - timedelta(days=1)).date()

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
    """
    Loads and validates input files based on configuration.
    File configurations: Define sheet names, headers, and required columns
    """
    dataframes = {}
    input_folder = Path(ConfigConstants.INPUT_FOLDER)
    output_folder = Path(ConfigConstants.OUTPUT_FOLDER)

    file_configs = {
        'Transaction Summary 86033': {
            'filename': config_data['transactionsummary_86033'],
            'subfolder': ConfigConstants.SUBFOLDER_86033,
            'headerrow': 'Transaction Particulars',
            'sheet_name': 'Sheet0',
            'required_columns': ['Transaction Particulars', 'Value Date', 'Amount(INR)', 'DR|CR'],
        },
        'BRS 86033': {
            'filename': config_data['brs_86033'],
            'subfolder': ConfigConstants.SUBFOLDER_86033,
            'headerrow': 'Date',
            'sheet_name': t_2_date,
            'required_columns': ['Particulars', 'Date', 'Amount'],
            'output_folder': output_folder / ConfigConstants.SUBFOLDER_86033,
        },
        'AFL_GL_Interface_Staging_Data': {
            'filename': config_data['AFL_GL_Interface_Staging_Data'],
            'subfolder': ConfigConstants.SUBFOLDER_86033,
            'headerrow': 'Accounting Code',
            'sheet_name': 'AFL_GL_Interface_Staging_Data_1',
            'required_columns': [
                'Accounting Code', 'Debit Amount', 'Credit Amount',
                'Additional Field 1', 'Additional Field 2',
                'Additional Field 3', 'Additional Field 4', 'Additional Field 5'
            ],
        },
        'Bank_Book_Data': {
            'filename': config_data['bank_book_86033'],
            'subfolder': ConfigConstants.SUBFOLDER_86033,
            'headerrow': 'Particulars',
            'sheet_name': "Dec'24",
            'required_columns': ['Particulars', 'Date'],
        },
        'BBPS_Data': {
            'filename': config_data['bbps_file'],
            'subfolder': ConfigConstants.SUBFOLDER_86033,
            'headerrow': 'TXNDATE',
            'sheet_name': 'Table',
            'required_columns': ['TXNREFERENCEID', 'TXNDATE', 'TXNAMOUNT', 'CLIENT_CODE'],
        },
        'Cash_Data': {
            'filename': config_data['cash_file'],
            'subfolder': ConfigConstants.SUBFOLDER_86033,
            'headerrow': 'LOAN_ACCOUNT_NUMBER',
            'sheet_name': 'Table1',
            'required_columns': ['LOAN_ACCOUNT_NUMBER', 'TOTL_AMNT', 'CUSTOMER_NAME', 'TRNSCTN_MODE'],
        },
        'UPI_Data': {
            'filename': config_data['upi_file'],
            'subfolder': ConfigConstants.SUBFOLDER_86033,
            'headerrow': 'DEBIT_AMOUNT',
            # 'sheet_name': 'UPI_File',
            'sheet_name': 'UPI_Sett_AXIS FINANCE LIMITED_2',          
            'required_columns': ['DEBIT_AMOUNT', 'ACCOUNT_CUST_NAME', 'UNQ_CUST_ID', 'MERCHANT_ID'],
        },
    }

    def load_and_validate(file_key, file_config):
        """Helper function to load and validate a file."""
        try:
            # Build file path
            file_path = input_folder / file_config['subfolder'] / file_config['filename']
            general_logger.info(f"Loading {file_key} from {file_path}")

            # Load file
            df = load_file(file_path, headerrow=file_config['headerrow'], sheet_name=file_config['sheet_name'])

            # Validate required columns
            if not check_columns_exists(
                df, file_config['required_columns'], file_key, session, email_to, file_path
            ):
                general_logger.error(f"Validation failed for {file_key} (File: {file_path})")
                return None

            # Copy file to output folder if specified
            if 'output_folder' in file_config:
                os.makedirs(file_config['output_folder'], exist_ok=True)
                shutil.copy(file_path, file_config['output_folder'])

            general_logger.info(f"{file_key} validated successfully (File: {file_path})")
            return df
        except FileNotFoundError as e:
            print(e)
            error_logger.error(f"{file_key} file not found: {e}")
            # file_not_found_error(session, "File Loading", ConfigConstants.SHARED_FOLDER, file_config['filename'], email_to)
        except Exception as e:
            error_logger.error(f"Error while loading {file_key}: {e}")
            traceback.print_exc()
        return None

    # Process each file configuration
    for file_key, file_config in file_configs.items():
        df = load_and_validate(file_key, file_config)
        if df is None:
            return None  # Exit if any file fails validation
        dataframes[file_key] = df

    return dataframes

def generate_transaction_report(transaction_df, bbps_df, valuedate, output_folder):
    """
    Generates a BRS (Bank Reconciliation Statement) report by filtering transactions
    for a specific 'Value Date' and performing transformations, including updating remarks 
    and extracting flags. Saves the report to the specified output file.

    Args:
        transaction_df (DataFrame): The transaction DataFrame.
        bbps_df (DataFrame): The BBPS DataFrame.
        valuedate (str): The 'Value Date' to filter transactions on.
        output_folder (str): The folder to save the report.

    Returns:
        tuple: Filtered transaction DataFrame, closing balance, and contra data DataFrame.
    """
    try:
        # Filter transactions by 'Value Date'
        filtered_df = transaction_df[transaction_df['Value Date'] == valuedate]
        if filtered_df.empty:
            general_logger.warning("No transactions found for the specified Value Date.")
            closing_balance = 0
        else:
            closing_balance = filtered_df['Balance(INR)'].iloc[-1]
            # closing_balance = 0


        filtered_df['Amount(INR)']= pd.to_numeric(filtered_df['Amount(INR)'], errors = 'coerce')
        # Update remarks based on transaction particulars
        filtered_df.loc[
            filtered_df['Transaction Particulars'].str.endswith("607-"),
            ['Remarks', 'Final Remarks']
        ] = "Contra"

        # Filter for cash and cheque transactions
        # cash_pattern = r'Axis Finance LTD Cash fund \d{2}\.\d{2}\.\d{4}'
        # cheque_pattern = r'Axis Finance LTD Chq fund \d{2}\.\d{2}\.\d{4}'

        cash_pattern = r'AXIS FINANCE LTD CASH FUND'
        cheque_pattern = r'AXIS FINANCE LTD Chq FUND'

        filtered_cash = filtered_df[filtered_df['Transaction Particulars'].str.contains(cash_pattern, regex=True)]
        filtered_cheque = filtered_df[filtered_df['Transaction Particulars'].str.contains(cheque_pattern, regex=True)]

        if not filtered_cash.empty or not filtered_cheque.empty:
            cash_filtered_df = pd.concat([filtered_cash, filtered_cheque])
            # filtered_df.loc[cash_filtered_df.index, 'Remarks'] = 'Cash'
            filtered_df.loc[filtered_df.index.isin(cash_filtered_df.index), 'Remarks'] = 'Cash'

           

        # Filter for BBPS transactions
        filtered_bbps = filtered_df[filtered_df['Transaction Particulars'].str.startswith('BBPS')]
        filtered_df.loc[filtered_bbps.index, 'Remarks'] = 'BBPS'

        # Extract contra data and add 'System' column
        contra_data = filtered_df[filtered_df['Remarks'].str.contains('Contra', na=False)].copy()
        contra_data['System'] = 'Treasury'

        # Validate BBPS totals
        total_txn_amount = bbps_df['TXNAMOUNT'].sum()
        total_amount_inr = filtered_bbps['Amount(INR)'].sum()

        print(f"Total 'TXNAMOUNT' in downloaded file: {total_txn_amount}")
        print(f"Total 'Amount INR' in 'Transaction Summary' for 'BBPS': {total_amount_inr}")
        if total_txn_amount == total_amount_inr:
            print("The total amounts match.")
        else:
            print("The total amounts do not match.")

        # #  removee itt afterward Save the filtered DataFrame to Excel
        # output_file = Path(output_folder) / "86033" / "transaction1.xlsx"
        # output_file.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        # filtered_df.to_excel(output_file, index=False)
        # general_logger.info(f"Transaction report saved to {output_file}")

        return filtered_df, closing_balance, contra_data

    except Exception as e:
        error_logger.error(f"Error while generating the transaction report: {e}")
        traceback.print_exc()
        return None, 0, None

def generate_interface_report(afl_gl_interface_staging_data_df):
    """
    Filters data for rows with an 'Accounting Code' of 221222, computes subtotals 
    for debit and credit amounts, and creates a 'Working1' column with concatenated 
    information from 'Debit Amount' or 'Credit Amount' and 'Additional Field 2'.
    
    Args:
        afl_gl_interface_staging_data_df (DataFrame): Input DataFrame with GL interface data.

    Returns:
        tuple: A tuple containing:
            - debit_subtotal (float): Sum of 'Debit Amount'.
            - credit_subtotal (float): Sum of 'Credit Amount'.
            - afl_filtered_df (DataFrame): Filtered and transformed DataFrame.
    """
    try:
        # Filter rows where 'Accounting Code' equals 221222
        afl_filtered_df = afl_gl_interface_staging_data_df[
            afl_gl_interface_staging_data_df['Accounting Code'] == 221222
        ].copy()

        if afl_filtered_df.empty:
            general_logger.warning("No rows found with 'Accounting Code' = 221222.")
            return 0, 0, afl_filtered_df



        afl_filtered_df['Credit Amount']= pd.to_numeric(afl_filtered_df['Credit Amount'], errors = 'coerce')
        afl_filtered_df['Credit Amount']= afl_filtered_df['Credit Amount'].astype('Int64')
        afl_filtered_df['Debit Amount']= pd.to_numeric(afl_filtered_df['Debit Amount'], errors = 'coerce')
        afl_filtered_df['Debit Amount']= afl_filtered_df['Debit Amount'].astype("Int64")

        # Create 'Working1' column by combining relevant fields
        afl_filtered_df['Working1'] = afl_filtered_df.apply(
            lambda row: f"{row['Debit Amount']}{row['Additional Field 2']}" if pd.notnull(row['Debit Amount'])
            else f"{row['Credit Amount']}{row['Additional Field 2']}",
            axis=1
        )
        

        # Calculate subtotals for debit and credit amounts
        debit_subtotal = afl_filtered_df['Debit Amount'].sum(skipna=True)
        credit_subtotal = afl_filtered_df['Credit Amount'].sum(skipna=True)

        general_logger.info(
            f"Interface Report Generated: Debit Subtotal = {debit_subtotal}, Credit Subtotal = {credit_subtotal}"
        )
        return debit_subtotal, credit_subtotal, afl_filtered_df

    except Exception as e:
        error_logger.error(f"Error generating interface report: {e}")
        traceback.print_exc()
        return 0, 0, pd.DataFrame()

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
            'System': ['Indus', 'Indus']
        }

        # Create a DataFrame for new rows
        new_df = pd.DataFrame(new_data)

        # Process contra data
        contra_data['Credit'] =contra_data.apply(lambda x: x['Amount(INR)'] if x['DR|CR']=='DR' else 0, axis=1)
        contra_data['Debit'] =contra_data.apply(lambda x: x['Amount(INR)'] if x['DR|CR']=='CR' else 0, axis=1)

        contra_data = contra_data[['Value Date','Credit', 'Debit', 'Transaction Particulars', 'System']].copy()
        contra_data.columns = ['Date', 'Credit','Debit', 'Particulars', 'System']
        
        contra_data = contra_data[['Date', 'Particulars', 'Debit', 'Credit', 'System']]  # Reorder columns
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
        # output_path = Path(output_folder) / '6033' / 'bank_book.xlsx'
        output_path = os.path.join(output_folder, ConfigConstants.SUBFOLDER_86033, 'bank_book.xlsx')
        bank_book_df.to_excel(output_path, index=False)
        general_logger.info(f"Bank Book report saved successfully at {output_path}")

        return book_balance

    except Exception as e:
        error_logger.error(f"Error in generating Bank Book report: {e}")
        traceback.print_exc()
        return bank_book_df  # Return original DataFrame in case of error


def match_and_reconcile_bbps(bbps_df, brs_df, afl_df, transaction_df):
    """
    Matches and reconciles BBPS data with transaction, AFL, and BRS records.

    Args:
        bbps_df (DataFrame): DataFrame containing BBPS transaction data.
        brs_df (DataFrame): DataFrame containing BRS (Bank Reconciliation Statement) data.
        afl_df (DataFrame): DataFrame containing AFL GL Interface Staging data.
        transaction_df (DataFrame): DataFrame containing transaction summary.

    Returns:
        tuple: Updated `afl_df` and `brs_df` after reconciliation.
    """
    try:
        # Match rows in `brs_df` based on 'Internal Remarks' and 'TXNREFERENCEID' from `bbps_df`
        matching_rows = brs_df[brs_df['Internal Remarks'].isin(bbps_df['TXNREFERENCEID'])]
        total_amount_brs = matching_rows['Amount'].sum()

        # Create a unique key 'FD' in `bbps_df` for merging
        bbps_df['FD'] = bbps_df.apply(
            lambda row: ''.join(str(col) if pd.notnull(col) else '' for col in [int(row['TXNAMOUNT']), row['CLIENT_CODE']]),
            axis=1
        )

        # Merge `afl_df` with `bbps_df` based on the unique keys
        merged_data = pd.merge(afl_df, bbps_df[['FD']], left_on='Working1', right_on='FD', how='left')
        afl_df['Working'] = merged_data['FD']

        # Filter reconciled rows from `afl_df`
        afl_filtered_df = afl_df[
            afl_df['Working'].notna() & 
            (~afl_df['Additional Field 5'].str.contains('Cheque', na=False))
        ]
        total_credit = afl_filtered_df['Credit Amount'].sum()
        total_debit = afl_filtered_df['Debit Amount'].sum()

        # Summarize BBPS transactions in `transaction_df`
        bbps_summary = transaction_df[transaction_df['Remarks'] == 'BBPS']
        total_amount_inr = bbps_summary['Amount(INR)'].sum()

        # Log the comparison result for totals
        print(f"Total Credit: {total_credit}, Total Debit: {total_debit}, Total Amount (BRS): {total_amount_brs}, Total Amount (BBPS Summary): {total_amount_inr}")
        comparison_result = float(total_credit + total_debit + total_amount_brs) == float(total_amount_inr)
        print(f"Reconciliation Successful: {comparison_result}")

        # Update remarks and remove matched rows if totals match
        if comparison_result:
            afl_df.loc[afl_filtered_df.index, 'Remarks'] = 'Clr from BBPS'
            brs_df = brs_df[~brs_df['Internal Remarks'].isin(bbps_df['TXNREFERENCEID'])]
        
        return afl_df, brs_df

    except Exception as e:
        error_logger.error(f"Error in BBPS matching and reconciliation: {e}")
        traceback.print_exc()
        return afl_df, brs_df

def match_and_reconcile_cash(transaction_df, cash_df, afl_df):
    """
    Matches and reconciles cash transactions between Transaction Summary, Cash Data, 
    and AFL_GL_Interface_Staging_Data.

    Args:
        transaction_df (DataFrame): Transaction summary containing remarks and amounts.
        cash_df (DataFrame): Cash data with loan account numbers and amounts.
        afl_df (DataFrame): AFL GL Interface Staging Data with financial records.

    Returns:
        tuple: Updated `afl_df` and `cash_df` with reconciliation remarks.
    """
    try:
        # Create a unique 'Working' key in cash_df for matching
        cash_df['Working'] = cash_df.apply(
            lambda row: ''.join(str(col) if pd.notnull(col) else '' for col in 
                                [int(row['TOTL_AMNT']), row['LOAN_ACCOUNT_NUMBER']]), axis=1
        )

        # Filter cash transactions from transaction_df
        cash_transactions = transaction_df[transaction_df['Remarks'].str.contains('Cash', na=False)]
        print(cash_transactions)
        total_cash_amount_transaction = cash_transactions['Amount(INR)'].sum()
        total_cash_amount_cash = cash_df['TOTL_AMNT'].sum()

        # Log totals for comparison
        print(f"Total Cash Amount in Transaction Summary: {total_cash_amount_transaction}")
        print(f"Total Cash Amount in Cash Data: {total_cash_amount_cash}")

        if total_cash_amount_transaction == total_cash_amount_cash:
            print("Cash amounts match.")
        else:
            print("Cash amounts do not match.")
        
        # Match entries in AFL_GL_Interface_Staging_Data with cash data
        matched_data = afl_df[afl_df['Working1'].isin(cash_df['Working'])]

        # exit()


        # Identify mismatched entries in cash_df
        mismatched_data = cash_df[~cash_df['Working'].isin(afl_df['Working1'])]

        # Update remarks for matched entries in afl_df
        afl_df.loc[matched_data.index, 'Remarks'] = 'Cash 07'

        # Update remarks for mismatched entries in cash_df
        cash_df.loc[mismatched_data.index, 'Remarks'] = 'Open'

        # Add mismatched data to the reconciliation file (e.g., BRS)
        mismatched_to_append = mismatched_data[['CUSTOMER_NAME','LOAN_ACCOUNT_NUMBER', 'TOTL_AMNT']]
        mismatched_to_append.columns = ['Particulars','Loan Account Number', 'Amount']

        return afl_df, mismatched_to_append
    except Exception as e:
        error_logger.error(f"Error in cash reconciliation: {e}")
        traceback.print_exc()
        return afl_df, cash_df

def match_reconcile_upi(brs_df, upi_df, transaction_df):
    """
    Matches and reconciles data between BRS, UPI, and Transaction Summary dataframes.

    Args:
        brs_df (DataFrame): Bank Reconciliation Statement DataFrame.
        upi_df (DataFrame): UPI transaction data.
        transaction_df (DataFrame): Transaction summary data.

    Returns:
        DataFrame: Updated BRS DataFrame with reconciled data.
    """
    try:
        # Filter out rows with 'Cash', 'BBPS', or 'Contra' in Remarks
        # filtered_transaction_summary = transaction_df[
        #     ~transaction_df['Remarks'].str.contains('Cash|BBPS|Contra', na=False)
        # ].copy()

        filtered_transaction_summary = transaction_df[
            ~transaction_df['Remarks'].str.contains('Cash|BBPS|Contra', na=False)
        ].copy()

        # Adjust the amount sign based on the DR|CR column
        filtered_transaction_summary['Amount'] = filtered_transaction_summary.apply(
            lambda row: -row['Amount(INR)'] if pd.notnull(row['Amount(INR)']) and 
                        row['DR|CR'].strip().upper() == 'DR' else row['Amount(INR)'], axis=1)

        # Assign final remarks based on the amount's sign
        # filtered_transaction_summary['Final Remark'] = filtered_transaction_summary['Amount'].apply(
        #     lambda row: 'Debit in Bank Statement - Not in system' if row['DR|CR'].strip().upper() == 'DR' 
        #               else 'Credit in Bank Statement - Not in system')
        filtered_transaction_summary['Final Remark'] = filtered_transaction_summary.apply(
            lambda row: 'Debit in Bank Statement - Not in system' if row['DR|CR'].strip().upper() == 'DR' else 'Credit in Bank Statement - Not in system',
            axis=1)

        # Select and rename relevant columns
        transaction_data = filtered_transaction_summary[['Value Date', 'Transaction Particulars', 'Amount','Final Remark']]
        transaction_data.columns = ['Date', 'Particulars', 'Amount','Final Remark']

        
        transaction_data['Additional Remarks'] = 'Pending from operation'

        # Append transaction data to the BRS DataFrame
        brs_df = pd.concat([brs_df, transaction_data], ignore_index=True)

        # Generate the 'Working' key for reconciliation
        brs_df['Working'] = brs_df.apply(
            lambda row: ''.join(str(col) if pd.notnull(col) else '' for col in 
                                [(row['Amount']), row['Internal Remarks']]), axis=1
        )

        # Apply the reference extraction function to create 'Working BBPS'
        brs_df['Particulars'] = brs_df['Particulars'].fillna('').astype(str)
        brs_df['Working BBPS'] = brs_df['Particulars'].apply(extract_reference_brs)

        # Filter for UPI payments on the specific date
        upi_filtered_df = brs_df[brs_df['Particulars'].str.contains(f'UPI payment {t_1_date}', case=False, na=False)]

        # Calculate total UPI amounts from BRS and UPI data
        brs_upi_amount = upi_filtered_df['Amount'].sum()
        upi_amount = upi_df['DEBIT_AMOUNT'].sum()

        # Log the comparison result
        if brs_upi_amount == upi_amount:
            print(f"UPI Amounts Match: {brs_upi_amount} == {upi_amount}")
        else:
            print(f"UPI Amounts Mismatch: {brs_upi_amount} != {upi_amount}")
        

        # Merge the two dataframes on a common key, if necessary
        # upi_df = upi_df.merge(upi_filtered_df[['Particulars']], left_index=True, right_index=True)
        upi_df['Particulars']= f"AXIS FINANCE LIMITED UPI Payment {t_1_date}"
        
        # Then create the 'Working' column
        upi_df['Working'] = upi_df.apply(
            lambda row: ''.join(
                str(col) if pd.notnull(col) else '' 
                for col in [row['Particulars'], row['ACCOUNT_CUST_NAME']]),
            axis=1)

        upi_df['Final Remark']= 'Credit in Bank Statement - Not in system'

        # Prepare UPI data for appending
        filter_upi_data = upi_df[['TXN_DATE', 'Working', 'DEBIT_AMOUNT', 'RRN', 'Final Remark']].copy()
        filter_upi_data.columns = ['Date', 'Particulars', 'Amount', 'Internal Remarks','Final Remark']

      

        # Remove already reconciled UPI transactions from BRS
        brs_df = brs_df[~brs_df['Particulars'].str.contains(f'UPI payment {t_1_date}', case=False, na=False)]

        # Append the filtered UPI data to the BRS DataFrame
        brs_df = pd.concat([brs_df, filter_upi_data], ignore_index=True)

    
        # brs_df.to_excel(rf'{output_folder}\86033\brsssdata.xlsx', index=False)


        # Return the updated BRS DataFrame
        return brs_df

    except Exception as e:
        error_logger.error(f"Error during BRS reconciliation: {e}")
        traceback.print_exc()
        return brs_df



# Extract reference number based on the conditions
def extract_reference_brs(particular):
    parts = particular.split('/')
    if 'IMPS' in particular:
        return parts[2] if len(parts) > 2 else None  
    elif 'RTGS' in particular or 'NEFT' in particular:
        return parts[1] if len(parts) > 1 else None
    return None

# def extract_reference_brs(particular):
#     parts = particular.split('/')
#     if 'IMPS' in particular:
#         return parts[2] if len(parts) > 2 else None  
#     elif 'RTGS' in particular or 'NEFT' in particular:
#         return parts[1] if len(parts) > 1 else None
#     return particular


def match_reconcile_brs_afl(brs_df, afl_df, previous_date):
    """
    Function to reconcile BRS and AFL dataframes and return a consolidated dataframe
    with calculated aging and additional remarks.
    
    Parameters:
        brs_df (pd.DataFrame): Bank Reconciliation Statement dataframe.
        afl_df (pd.DataFrame): AFL_GL_Interface_Staging_Data dataframe.
        previous_date (datetime): Reference date for aging calculation.
        
    Returns:
        pd.DataFrame: Consolidated dataframe with reconciled records.
    """
    try:
        # Filter AFL rows where 'Remarks' is blank or missing
        filtered_afl = afl_df[afl_df['Remarks'].isna() | (afl_df['Remarks'] == '')]

        # Match AFL 'Additional Field 5' with BRS 'Working BBPS'
        matched_data_afl = filtered_afl[filtered_afl['Additional Field 5'].isin(brs_df['Working BBPS'])]
        
        # Remove matched records from BRS dataframe
        brs_df = brs_df[~brs_df['Working BBPS'].isin(filtered_afl['Additional Field 5'])]

        # Update 'Remarks' column in AFL for matched records
        afl_df.loc[matched_data_afl.index, 'Remarks'] = 'Clr from BRS'

        # Re-filter AFL rows where 'Remarks' is blank or missing after update
        filtered_afl = afl_df[afl_df['Remarks'].isna() | (afl_df['Remarks'] == '')]

        # Compute 'Amount' column based on 'Debit Amount' and 'Credit Amount'
        filtered_afl['Amount'] = filtered_afl.apply(
            lambda row: -row['Debit Amount'] if pd.notna(row['Debit Amount']) else row['Credit Amount'], axis=1
        )

        # Prepare AFL dataframe for concatenation
        filtered_afl = filtered_afl[['Accounting Date', 'Additional Field 3', 'Amount', 'Additional Field 2', 'Additional Field 5']]
        filtered_afl.columns = ['Date', 'Particulars', 'Amount', 'Loan No.', 'Internal Remarks']

        # Add 'Final Remark' column based on 'Amount'
        filtered_afl['Final Remark'] = filtered_afl['Amount'].apply(
            lambda x: 'Debit in system - Not in Bank Statement' if x < 0 else 'Credit in system - Not in Bank Statement'
        )

        # Concatenate BRS and modified AFL dataframes
        consolidated_df = pd.concat([brs_df, filtered_afl], ignore_index=True)

        # Convert 'Date' to datetime format
        consolidated_df['Date'] = pd.to_datetime(consolidated_df['Date'], format='%d-%m-%Y', errors='coerce')

        # Calculate 'Aging' as the difference between reference date and transaction date
        consolidated_df['Aging'] = (pd.Timestamp(previous_date) - consolidated_df['Date']).dt.days

        # Apply aging bucket categorization
        consolidated_df['Aging Bucket'] = consolidated_df['Aging'].apply(get_aging_bucket)

        # Add additional remarks
        consolidated_df['Additional Remarks'] = 'Pending from operation'

        return consolidated_df

    except KeyError as e:
        print(f"KeyError: Missing column in the input DataFrame - {e}")
    except ValueError as e:
        print(f"ValueError: Data format issue - {e}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")

    # Return an empty DataFrame in case of an error
    return pd.DataFrame()


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


def compute_final_summary(brs_86033_df, closing_balance,book_balance):
    """Compute the final summary for the report."""
    brs_86033_df['Amount'] = pd.to_numeric(brs_86033_df['Amount'], errors='coerce')

    total_value = (book_balance +
        get_total(brs_86033_df, 'Debit in Bank Statement - Not in system') +
        get_total(brs_86033_df, 'Credit in Bank Statement - Not in system') +
        get_total(brs_86033_df, 'Debit in system - Not in Bank Statement') +
        get_total(brs_86033_df, 'Credit in system - Not in Bank Statement')
    )
    summary_data = {
        'Description': ['Bank', 'A/C No.', 'Book Balance-BB', 'Debit in System - Not in Bank Statement', 
                        'Credit in System - Not in Bank Statement', 'Debit in Bank Statement - Not in system', 
                        'Credit in Bank Statement - Not in system', 'Balance as per Bank (Computed)', 
                        'Balance as per Bank Statement', 'Difference'],
        'Value': ['AXIS BANK – RETAIL COLLECTION A/C ', '918020079086033', book_balance, 
                get_total(brs_86033_df, 'Debit in system - Not in Bank Statement'),
                get_total(brs_86033_df, 'Credit in system - Not in Bank Statement'),
                get_total(brs_86033_df, 'Debit in Bank Statement - Not in system'),
                get_total(brs_86033_df, 'Credit in Bank Statement - Not in system'),               
                total_value , closing_balance, float(total_value) - float(closing_balance)]
    }
    return pd.DataFrame(summary_data)

def get_total(df, remark):
    """Calculate total for given remark condition."""
    return df[df['Final Remark'].str.contains(remark, na=False)]['Amount'].sum()

def save_report(brs_output_file, final_summary_df, brs_86033_df):
    """Save the final report to an Excel file."""
    general_logger.info(f"Saving final report to {brs_output_file}")
    with pd.ExcelWriter(brs_output_file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        pd.DataFrame({"Column1": ["Axis Finance Limited"]}).to_excel(writer, sheet_name=t_1_date, index=False, header=False, startrow=0,startcol=1)
        final_summary_df.to_excel(writer, sheet_name=t_1_date, index=False, startrow=1, startcol=1, header=False)
        brs_86033_df.to_excel(writer, sheet_name=t_1_date, index=False, startrow=len(final_summary_df) + 3)
    color_excel(brs_output_file, t_1_date)

def main_account_86033(to_email:str):
    """
    Main function to execute the BRS process for 86033. 
    Loads input files, generates reports, and performs reconciliation.
    """
    try:
        start_mail(to_email,"Axis Finance BRS of Account 6033")


        try:
            sftp_handler_axis.sftp_hander(account_no = 6033)
        except Exception as e:
            print(f"Error occured in SFTP 6033")

        # Load input data
        dataframes = load_input_files(session, to_email, config_data)
        if not dataframes:
            general_logger.error("Failed to load input files. Exiting process.")
            return

        # Extract dataframes from the loaded data
        transaction_df = dataframes.get('Transaction Summary 86033')
        brs_df = dataframes.get('BRS 86033')
        afl_gl_df = dataframes.get('AFL_GL_Interface_Staging_Data')
        bank_book_df = dataframes.get('Bank_Book_Data')
        bbps_df = dataframes.get('BBPS_Data')
        cash_df = dataframes.get('Cash_Data')
        upi_df = dataframes.get('UPI_Data')



        # Validate mandatory dataframes
        if any(df is None for df in [transaction_df, brs_df, afl_gl_df, bank_book_df, bbps_df]):
            general_logger.error("Missing required dataframes. Exiting process.")
            return

        # Set output folder path
        output_folder = Path(ConfigConstants.OUTPUT_FOLDER)
        output_folder.mkdir(parents=True, exist_ok=True)
        brs_output_file = os.path.join(output_folder, ConfigConstants.SUBFOLDER_86033, config_data['brs_86033'])


        # Generate Transaction Report
        general_logger.info("Generating Transaction Report...")
        transaction_report, closing_balance, contra_data = generate_transaction_report(
            transaction_df=transaction_df,
            bbps_df=bbps_df,
            valuedate=valuedate,
            output_folder=output_folder
        )
        if transaction_report is None:
            general_logger.error("Failed to generate Transaction Report. Exiting process.")
            return

        # Generate Interface Report
        general_logger.info("Generating Interface Report...")
        debit_subtotal, credit_subtotal, afl_df = generate_interface_report(afl_gl_df)
        if afl_df is None:
            general_logger.error("Failed to generate Interface Report. Exiting process.")
            return

        # Generate Bank Book Report
        general_logger.info("Generating Bank Book Report...")
        book_balance = generate_bankbook_report(
            debit_subtotal=debit_subtotal,
            credit_subtotal=credit_subtotal,
            bank_book_df=bank_book_df,
            contra_data=contra_data
        )
        # if bank_book_report is None:
            # general_logger.error("Failed to generate Bank Book Report. Exiting process.")
            # return

        # Perform Matching and Reconciliation BBPS
        general_logger.info("Performing Matching and Reconciliationof BBPS...")
        
        afl_df, brs_df= match_and_reconcile_bbps(
            bbps_df=bbps_df,
            brs_df=brs_df,
            afl_df=afl_df,
            transaction_df=transaction_report
        )

        # Perform CASH Matching and Reconciliation
        general_logger.info("Performing Matching and Reconciliationof Cash...")
        afl_df, cash_df=match_and_reconcile_cash(transaction_report, cash_df, afl_df)


        # Perform UPI Matching and Reconciliation
        general_logger.info("Performing Matching and Reconciliationof UPI...")
        brs_df = match_reconcile_upi(brs_df, upi_df, transaction_report)


        # Perform BRS and AFL Matching and Reconciliation
        general_logger.info("Performing Matching and Reconciliationof BRS and AFL...")
        brs_86033_df =match_reconcile_brs_afl(brs_df, afl_df, previous_date=previousdate)

        
        brs_86033_df.to_excel(brs_output_file, index=False)



        final_summary_df = compute_final_summary(brs_86033_df, closing_balance,book_balance)

        save_report(brs_output_file, final_summary_df, brs_86033_df)
        general_logger.info("BRS process completed successfully.")


        output_path = os.path.join(output_folder, ConfigConstants.SUBFOLDER_86033, 'bank_book.xlsx')

        output_file =[brs_output_file,output_path]

        upload_file_sftp((output_file), "6033")

        success_mail(to_email, "Axis Finance BRS",output_file)

        result = f""" Account 86033 have been processed successfully!!
        BRS Output File: {brs_output_file}
        Bank Book Output File: {output_path}
        """
        status = "Success"
        return result, status

    except Exception as e:
        error_logger.error(f"Error in BRS process: {e}")
        handle_critical_error(session, "Axis Bank BRS Process", e, shared_folder, to_email)
        return f"Error in processing BRS for Account - 86033: {e}", "Failure"
