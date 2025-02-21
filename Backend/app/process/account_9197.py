import pandas as pd
from pathlib import Path
from app.init.config_loader import run as load_config
from app.config.constants import ConfigConstants
from app.db.db_engine import get_db_engine, get_session
from app.db.db_operations import insert_detail_log, insert_process_status
from app.utils.custom_logger import general_logger, error_logger
# from utils.error_utils import handle_critical_error, file_not_found_error
from app.utils.dataframe_utils import check_columns
from app.utils.excel_styles import color_excel
import os
import traceback
from datetime import datetime, timedelta
from app.process import sftp_handler_axis
import openpyxl
import shutil
from app.utils.load_utils import load_file
import sys
from app.init.email_service import start_mail, success_mail
from app.process.upload_to_sftp_server import upload_file_sftp



# Initialize date variables
current_date = datetime.now()
valuedate = (current_date - timedelta(days=1)).strftime('%d-%m-%Y')
t_1_date = (current_date - timedelta(days=1)).strftime('%d.%m.%y')
t_2_date = (current_date - timedelta(days=2)).strftime('%d.%m.%y')

previousdate = (current_date - timedelta(days=1)).date()

# Initialize session and load configuration
session = get_session(get_db_engine())
config_data = load_config()
shared_folder = Path(ConfigConstants.INPUT_FOLDER)
# email_to = config_data['email_to']

def check_columns_exists(df, expected_columns, file_type, session, email_to, filepath):
    """Check for required columns in the DataFrame."""
    return check_columns(df, expected_columns, file_type, session, email_to, filepath)

def load_input_files(session, email_to, config_data):
    """Loads and validates input files."""
    dataframes = {}
    input_folder = Path(ConfigConstants.INPUT_FOLDER)
    transactionsummary_file = config_data['transactionsummary_9197']
    brs_file = config_data['brs_9197']
    output_folder = Path(ConfigConstants.OUTPUT_FOLDER)
    brs_output_file = os.path.join(output_folder, brs_file)

    try:
        # Load Transaction Summary file
        transactionsummary_filepath = input_folder /ConfigConstants.SUBFOLDER_9791/ transactionsummary_file
        general_logger.info(f"Loading Transaction Summary 9197 from {transactionsummary_filepath}")
        transactionsummary_df = load_file(transactionsummary_filepath, headerrow='Transaction Particulars', sheet_name='Sheet0')

        # Validate Transaction Summary columns
        if not check_columns_exists(transactionsummary_df, 
                                     ['Transaction Particulars', 'Value Date', 'Amount(INR)', 'DR|CR'], 
                                     'Transaction Summary 9197', session, email_to, transactionsummary_filepath):
            general_logger.error(f"Validation failed for Transaction Summary 9197 (File: {transactionsummary_filepath})")
            return None
        
        dataframes['Transaction Summary 9197'] = transactionsummary_df
        general_logger.info(f"Transaction Summary 9197 validated successfully (File: {transactionsummary_filepath})")

        # Load and validate BRS file
        brs_filepath = input_folder /ConfigConstants.SUBFOLDER_9791/ brs_file
        brs_output_folder= os.path.join(output_folder,ConfigConstants.SUBFOLDER_9791)

        general_logger.info(f"Loading BRS 9197 from {brs_filepath}")
        brs_9197_df = load_file(brs_filepath, headerrow='Date', sheet_name=t_2_date)
        shutil.copy(brs_filepath,brs_output_folder)


        if not check_columns_exists(brs_9197_df, 
                                     ['Particulars', 'Date', 'Amount'], 
                                     'BRS 9197', session, email_to, brs_filepath):
            general_logger.error(f"Validation failed for BRS 9197 (File: {brs_filepath})")
            return None
        
        dataframes['BRS 9197'] = brs_9197_df
        general_logger.info(f"BRS 9197 validated successfully (File: {brs_filepath})")

        insert_detail_log(session, "Axis Finance Bank Reconciliation Process", "Axis Finance BRS Task", "N/A",
                            'BRS.AutoMail@axisfinance.in', f'N/A', f"Created Folder Structure of 9197", loglevel="Info")

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
        # file_not_found_error(session, "File Loading", shared_folder, transactionsummary_file, email_to)
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



def generate_brs_report(transaction_summary_df, brs_9197_df, brs_output_file):
    try:
        filtered_df = transaction_summary_df[transaction_summary_df['Value Date'] == valuedate]
        closing_balance = filtered_df['Balance(INR)'].iloc[-1] if not filtered_df.empty else 0
        closing_balance=0 #remove  line afterwardd

        # Filter the necessary columns from the Transaction Summary
        filtered_df = filtered_df[['Value Date', 'Transaction Particulars', 'Amount(INR)', 'DR|CR']].copy()
        # Create 'Amount' column based on 'DR|CR'
        filtered_df['Amount'] = filtered_df.apply(
            lambda row: -row['Amount(INR)'] if str(row['DR|CR']).strip().upper() == 'DR' else row['Amount(INR)'], axis=1)

        # Final Remark based on Amount
        # filtered_df['Final Remark'] = filtered_df.apply(
        #     lambda row: 'Debit in Bank Statement - Not in system' if float(row['Amount']) < 0 else 'Credit in Bank Statement - Not in system',
        #     axis=1
        # )

        filtered_df['Final Remark'] = filtered_df.apply(
            lambda row: 'Debit in Bank Statement - Not in system' if str(row['DR|CR']).strip().upper() == 'DR' else 'Credit in Bank Statement - Not in system',
            axis=1
        )
        filtered_df['Additional Remarks'] = 'Pending from operation'

        # Filter the necessary columns from the Transaction Summary
        transaction_filtered = filtered_df[['Value Date', 'Transaction Particulars', 'Amount', 'Final Remark','Additional Remarks']]

        # Rename the columns to match the BRS file
        transaction_filtered.rename(columns={
            'Value Date': 'Date',
            'Transaction Particulars': 'Particulars',
        }, inplace=True)

        # Append new rows to brs_9197_df
        brs_9197_df = pd.concat([brs_9197_df, transaction_filtered])

        previous_date_dt = pd.Timestamp(previousdate)

        # Convert 'Value Date' to datetime and calculate Aging
        brs_9197_df['Date'] = pd.to_datetime(
            brs_9197_df['Date'], format='%d-%m-%Y', errors='coerce', dayfirst=True)

        brs_9197_df['Aging'] = (previous_date_dt - brs_9197_df['Date']).dt.days

        # Aging Bucket categorization
        def aging_bucket(aging_days):
            if aging_days < 0:
                return 'Future Date'
            elif aging_days <= 30:
                return '0 to 30 days'
            elif aging_days <= 60:
                return '30 to 60 days'
            elif aging_days <= 90:
                return '60 to 90 days'
            else:
                return '90 days & above'

        brs_9197_df['Aging Bucket'] = brs_9197_df['Aging'].apply(aging_bucket)


        # Summing up Amounts
        brs_9197_df['Amount'] = pd.to_numeric(brs_9197_df['Amount'], errors='coerce')
        total_debit_in_bank = brs_9197_df[brs_9197_df['Final Remark'].str.contains('Debit in Bank Statement', na=False,case=False)]['Amount'].sum()
        total_credit_in_bank = brs_9197_df[brs_9197_df['Final Remark'].str.contains('Credit in Bank Statement', na=False,case=False)]['Amount'].sum()

        balance_as_per_bank_Computed = total_credit_in_bank + total_debit_in_bank

        # Data to be included in the DataFrame
        data = {
            'Description': [
                'Bank',
                'A/C No.', 
                'Book Balance-BB', 
                'Debit in System - Not in Bank Statement', 
                'Credit in System - Not in Bank Statement', 
                'Debit in Bank Statement - Not in system', 
                'Credit in Bank Statement - Not in system', 
                'Balance as per Bank (Computed)', 
                'Balance as per Bank Statement', 
                'Difference'
            ],
            'Value': [
                'Axis Bank LAS Fee Collection A/c',
                '919020036409197',
                None,
                None,  # Debit in System - Not in Bank Statement
                None,  # Credit in System - Not in Bank Statement
                total_debit_in_bank,  # Debit in Bank Statement - Not in system
                total_credit_in_bank,  # Credit in Bank Statement - Not in system
                balance_as_per_bank_Computed,  # Balance as per Bank (Computed)
                closing_balance,  # Placeholder for Balance as per Bank Statement
                balance_as_per_bank_Computed - closing_balance  ,  # Difference
            ]
        }
        df = pd.DataFrame(data)
        
        # Save to output file
        general_logger.info(f"Saving final report to {brs_output_file}")
        with pd.ExcelWriter(brs_output_file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            pd.DataFrame({"Column1": ["Axis Finance Limited"]}).to_excel(writer, sheet_name=t_1_date, index=False, header=False, startrow=0,startcol=1)
            # Write the DataFrame to the Excel file, start from row 2
            df.to_excel(writer, sheet_name=t_1_date, index=False, startrow=1,startcol=1,header=False)
            brs_9197_df.to_excel(writer,sheet_name=t_1_date,index=False,startrow=len(df)+3)

        insert_detail_log(session, "Axis Finance Bank Reconciliation Process", "Axis Finance BRS Task", "N/A",
                            'BRS.AutoMail@axisfinance.in', f'N/A', f"Working of Account 9197 is done", loglevel="Info")
    except Exception as e:
        e_type, e_obj, e_tb = sys.exc_info()
        print((str(e_tb.tb_lineno)))
        print('Exception Line Number - {0} , Exception Message - {1}'.format(str(e_tb.tb_lineno),e.__str__()))

        error_logger.error(f"Error in BRS process: {e}")
        
def main_account_9197(to_email:str):
    """Main function that runs the BRS process for 9197."""
    try:
        start_mail(to_email,"Axis Finance BRS of Account 9197")


        try:
            sftp_handler_axis.sftp_hander(account_no = 9197)
        except Exception as e:
            print(f"Error occured in SFTP 9197")

        dataframes = load_input_files(session, to_email, config_data)
        brs_file = config_data['brs_9197']

        if dataframes:
            transaction_summary_df = dataframes['Transaction Summary 9197']
            brs_9197_df = dataframes['BRS 9197']
            
            output_folder = Path(ConfigConstants.OUTPUT_FOLDER)
            brs_output_file = os.path.join(output_folder,ConfigConstants.SUBFOLDER_9791, brs_file)

            generate_brs_report(transaction_summary_df, brs_9197_df, brs_output_file)
            color_excel(brs_output_file,t_1_date)
            general_logger.info("BRS process completed successfully.")
            
            upload_file_sftp(([brs_output_file]), "9197")

            success_mail(to_email, "Axis Finance BRS",[brs_output_file])

            result = f""" Account 9197 have been processed successfully!!
            BRS Output File: {brs_output_file}
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
        # handle_critical_error(session, e, shared_folder, to_email)
        return f"Error in processing BRS for Account - 9197: {e}", "Failure"