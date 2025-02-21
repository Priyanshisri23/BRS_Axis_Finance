import pandas as pd
from pathlib import Path
from app.init.config_loader import run as load_config
from app.config.constants import ConfigConstants
from app.db.db_engine import get_db_engine, get_session
from app.utils.custom_logger import general_logger, error_logger
from app.db.db_operations import insert_detail_log, insert_process_status
from app.utils.error_utils import handle_critical_error, file_not_found_error
from app.utils.dataframe_utils import check_columns
from app.utils.excel_styles import color_excel
from app.utils.load_utils import load_file
from datetime import datetime, timedelta
from app.process import sftp_handler_axis
import shutil
import traceback
import sys
from app.init.email_service import start_mail,success_mail
from app.process.upload_to_sftp_server import upload_file_sftp
import os



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
    try:
        input_folder = Path(ConfigConstants.INPUT_FOLDER)
        output_folder = Path(ConfigConstants.OUTPUT_FOLDER)
       
        dataframes = {}

        # Load and validate files
        files_to_load = {
            'Transaction Summary 669': (config_data['transactionsummary_669'], 'Transaction Particulars', 'Sheet0'),
            'BRS 669': (config_data['brs_669'], 'Date', t_2_date),
            'AFL_GL_Interface_Staging_Data': (config_data['AFL_GL_Interface_Staging_Data'], 'Accounting Code', 'AFL_GL_Interface_Staging_Data_2'),
            'Bank Book 669': (config_data['bank_book_669'], 'Particulars', "Nov'24"),
        }

        for file_key, (file_name, header_row, sheet_name) in files_to_load.items():
            file_path = input_folder / ConfigConstants.SUBFOLDER_669 / file_name
            general_logger.info(f"Loading {file_key} from {file_path}")
            df = load_file(file_path, headerrow=header_row, sheet_name=sheet_name)

            if not validate_dataframe(df, file_key, session, email_to, file_path):
                return None

            dataframes[file_key] = df
            general_logger.info(f"{file_key} validated successfully.")

        insert_detail_log(session, "Axis Finance Bank Reconciliation Process", "Axis Finance BRS Task", "N/A",
                            'BRS.AutoMail@axisfinance.in', f'N/A', f"Created Folder Structure of 669", loglevel="Info")
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
        file_not_found_error(session, "File Loading", shared_folder, file_name, email_to)
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

def validate_dataframe(df, file_key, session, email_to, file_path):
    """Validate the loaded DataFrame for required columns."""
    try: 
        column_map = {
            'Transaction Summary 669': ['Transaction Particulars', 'Value Date', 'Amount(INR)', 'DR|CR'],
            'BRS 669': ['Particulars', 'Date', 'Amount'],
            'AFL_GL_Interface_Staging_Data': ['Accounting Code', 'Debit Amount', 'Credit Amount', 'Additional Field 1', 'Additional Field 2', 'Additional Field 3', 'Additional Field 4', 'Additional Field 5'],
            'Bank Book 669':['Date','Particulars','Vch Type','Debit','Credit']
        }

        expected_columns = column_map.get(file_key, [])
        return check_columns_exists(df, expected_columns, file_key, session, email_to, file_path)
    
    except Exception as e:
        e_type, e_obj, e_tb = sys.exc_info()
        print((str(e_tb.tb_lineno)))
        print('Exception Line Number - {0} , Exception Message - {1}'.format(str(e_tb.tb_lineno),e.__str__()))
        insert_detail_log(session, "Axis Finance Bank Reconciliation Process", "Axis Finance BRS Task", "N/A",
                            'BRS.AutoMail@axisfinance.in', f'{(str(e_tb.tb_lineno))}', f"{e.__str__()}", loglevel="Failed")
        insert_process_status(session, datetime.now(), "Axis Finance Bank Reconciliation Process",
                            "Axis Finance BRS Task", "N/A", 'BRS.AutoMail@axisfinance.in', "Failed", f"{e.__str__()}")
        error_logger.error(f"Error while Validating Dataframe: {e}")

def generate_brs_report(transaction_summary_df, brs_669_df, brs_output_file, interface_staging_data, bank_balance):
    """Generate and save the BRS report."""
    filtered_df = transaction_summary_df[transaction_summary_df['Value Date'] == valuedate]
    closing_balance = filtered_df['Balance(INR)'].iloc[-1] if not filtered_df.empty else 0
    # closing_balance=0 #remove  line afterwardd

    # Process Transaction Summary
    transaction_filtered = process_transaction_summary(filtered_df)

    # Append to BRS data and merge with interface staging data
    # brs_669_df = pd.concat([brs_669_df, transaction_filtered, interface_staging_data])
    # brs_669_df = pd.concat([brs_669_df.reset_index(drop=True), transaction_filtered.reset_index(drop=True), interface_staging_data.reset_index(drop=True)],ignore_index=True)

    # brs_669_df['Value Date'] = pd.to_datetime(brs_669_df['Value Date'], format='%d-%m-%Y', errors='coerce', dayfirst=True)
    
    
    # Check for duplicate indices
    for df, name in [(brs_669_df, "brs_669_df"), (transaction_filtered, "transaction_filtered"), (interface_staging_data, "interface_staging_data")]:
        if not df.index.is_unique:
            print(f"Duplicate index found in {name}")
 
    # Reset index
    brs_669_df = brs_669_df.reset_index(drop=True)
    transaction_filtered = transaction_filtered.reset_index(drop=True)
    interface_staging_data = interface_staging_data.reset_index(drop=True)
 
    # Align columns
    columns = brs_669_df.columns
    transaction_filtered = transaction_filtered.reindex(columns=columns, fill_value=0)
    interface_staging_data = interface_staging_data.reindex(columns=columns, fill_value=0)
 
    # Drop duplicates
    brs_669_df = brs_669_df.drop_duplicates()
    transaction_filtered = transaction_filtered.drop_duplicates()
    interface_staging_data = interface_staging_data.drop_duplicates()
 
    # Concatenate DataFrames
    brs_669_df = pd.concat([brs_669_df, transaction_filtered, interface_staging_data], axis=0, ignore_index=True)
 
    print(brs_669_df)
 
 
    # ===============================================================
    # brs_669_df['Value Date'] = pd.to_datetime(brs_669_df['Value Date'], format='%d-%m-%Y', errors='coerce', dayfirst=True)
    brs_669_df['Date'] = pd.to_datetime(brs_669_df['Date'], format='%d-%m-%Y', errors='coerce', dayfirst=True)
    brs_669_df['Aging'] = (pd.Timestamp(previousdate) - brs_669_df['Date']).dt.days
    brs_669_df['Aging Bucket'] = brs_669_df['Aging'].apply(get_aging_bucket)
    
    required_columns = [
        "Date", "Particulars", "Amount", "Internal Remarks",
        "Final Remark", "LOAN No", "Aging", "Aging Bucket", "Additional Remarks"]
    
    # Filter the DataFrame to keep only the specified columns
    # brs_669_df = brs_669_df.loc[:, required_columns]
    brs_669_df = brs_669_df[required_columns]

    # Compute summary and save the final report
    final_summary_df = compute_final_summary(brs_669_df, closing_balance, bank_balance)
    save_report(brs_output_file, final_summary_df, brs_669_df)


def process_transaction_summary(filtered_df):
    """Process the Transaction Summary DataFrame."""
    if filtered_df.empty:
        return filtered_df
    filtered_df['Amount'] = filtered_df.apply(
        lambda row: -row['Amount(INR)'] if row['DR|CR'].strip().upper() == 'DR' else row['Amount(INR)'], axis=1)
    
    filtered_df['Final Remark'] = filtered_df.apply(
        lambda row: 'Debit in Bank Statement - Not in system' if float(row['Amount']) < 0 else 'Credit in Bank Statement - Not in system', axis=1)

    # filtered_df['Value Date'] = pd.to_datetime(filtered_df['Value Date'], format='%d-%m-%Y', errors='coerce', dayfirst=True)
    # filtered_df['Aging'] = (pd.Timestamp(previousdate) - filtered_df['Value Date']).dt.days
    # filtered_df['Aging Bucket'] = filtered_df['Aging'].apply(get_aging_bucket)
    filtered_df['Additional Remarks'] = 'Pending from operation'

    return filtered_df[['Value Date', 'Transaction Particulars', 'Amount', 'Final Remark', 'Additional Remarks']]

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

def compute_final_summary(brs_669_df, closing_balance, bank_balance):
    """Compute the final summary for the report."""
    brs_669_df['Amount'] = pd.to_numeric(brs_669_df['Amount'], errors='coerce')

    total_value = (
        bank_balance +
        get_total(brs_669_df, 'Debit in Bank Statement - Not in system') +
        get_total(brs_669_df, 'Credit in Bank Statement - Not in system') +
        get_total(brs_669_df, 'Debit in system - Not in Bank Statement') +
        get_total(brs_669_df, 'Credit in system - Not in Bank Statement')
    )
    summary_data = {
        'Description': ['Bank', 'A/C No.', 'Book Balance-BB', 'Debit in System - Not in Bank Statement', 
                        'Credit in System - Not in Bank Statement', 'Debit in Bank Statement - Not in system', 
                        'Credit in Bank Statement - Not in system', 'Balance as per Bank (Computed)', 
                        'Balance as per Bank Statement', 'Difference'],
        'Value': ['Axis Bank Fee Collection A/C', '918020103490669', bank_balance, 
                  get_total(brs_669_df, 'Debit in system - Not in Bank Statement'),
                  get_total(brs_669_df, 'Credit in system - Not in Bank Statement'),
                  get_total(brs_669_df, 'Debit in Bank Statement - Not in system'),
                  get_total(brs_669_df, 'Credit in Bank Statement - Not in system'),
                  total_value , closing_balance, float(total_value) - float(closing_balance)]
    }
    return pd.DataFrame(summary_data)

def get_total(df, remark):
    """Calculate total for given remark condition."""
    return df[df['Final Remark'].str.contains(remark, na=False, case=False)]['Amount'].sum()

def save_report(brs_output_file, final_summary_df, brs_669_df):
    """Save the final report to an Excel file."""
    general_logger.info(f"Saving final report to {brs_output_file}")
    with pd.ExcelWriter(brs_output_file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        pd.DataFrame({"Column1": ["Axis Finance Limited"]}).to_excel(writer, sheet_name=t_1_date, index=False, header=False, startrow=0,startcol=1)
        final_summary_df.to_excel(writer, sheet_name=t_1_date, index=False, startrow=1, startcol=1, header=False)
        brs_669_df.to_excel(writer, sheet_name=t_1_date, index=False, startrow=len(final_summary_df) + 3, startcol=1)
    color_excel(brs_output_file, t_1_date)

def interface_filter(afl_gl_interface_staging_data_df):
    """Filter and process AFL GL Interface Staging Data."""
    filtered_df = afl_gl_interface_staging_data_df[afl_gl_interface_staging_data_df['Accounting Code'] == 221224]
    filtered_df['Amount'] = filtered_df.apply(
    lambda row: -row['Debit Amount'] if pd.notna(row['Debit Amount']) else row['Credit Amount'], axis=1)

    filtered_df = filtered_df[['Accounting Date', 'Additional Field 3', 'Amount', 'Additional Field 1', 'Additional Field 5']]
    filtered_df.columns = ['Date', 'Particulars', 'Amount', 'Loan Number', 'Internal Remarks']

    filtered_df['Final Remark'] = filtered_df.apply(
        lambda row: 'Debit in system - Not in Bank Statement' if row['Amount'] < 0 else 'Credit in system - Not in Bank Statement', axis=1)

    filtered_df['Date'] = pd.to_datetime(filtered_df['Date'], format='%d-%m-%Y', errors='coerce', dayfirst=True)
    filtered_df['Aging'] = (pd.Timestamp(previousdate) - filtered_df['Date']).dt.days
    filtered_df['Aging Bucket'] = filtered_df['Aging'].apply(get_aging_bucket)
    filtered_df['Additional Remarks'] = 'Pending from operation'

    return filtered_df

def bankbook_report(afl_gl_interface_staging_data_df,bank_book_669_df,output_folder):
    filtered_df = afl_gl_interface_staging_data_df[afl_gl_interface_staging_data_df['Accounting Code'] == 221224]
    filtered_df= filtered_df[['Accounting Date','Debit Amount','Credit Amount','Additional Field 3','Additional Field 5']]
    filtered_df.columns = ['Date','Debit','Credit','Particulars','Reference Number']
    
    # Set 'Vch Type' column: 'Payment' for Debits and 'Receipt' for Credits
    filtered_df['Vch Type'] = filtered_df.apply(lambda x: 'Receipt' if x['Debit'] > 0 else 'Payment', axis=1)
    bank_book_669_df = pd.concat([bank_book_669_df,filtered_df])

    bank_book_669_df['Net Balance'] = 0
    bank_book_669_df['Net Balance'] = bank_book_669_df['Net Balance'].loc[0]+(bank_book_669_df['Debit'].fillna(0) - bank_book_669_df['Credit'].fillna(0)).cumsum()
    book_balance = bank_book_669_df['Net Balance'].iloc[-1]
    bank_book_669_df.to_excel(fr"{output_folder}\{config_data['bank_book_669']}",index=False)

    return book_balance


def main_account_669(to_email:str):
    """Main function that runs the BRS process for Axis Finance."""
    try:
        start_mail(to_email,"Axis Finance BRS of Account 669")
        

        try:
            sftp_handler_axis.sftp_hander(account_no = 669)
        except Exception as e:
            print(f"Error occured in SFTP 669")

        dataframes = load_input_files(session, to_email, config_data)
        if not dataframes:
            sub_input_folder = Path(ConfigConstants.INPUT_FOLDER) / ConfigConstants.SUBFOLDER_669
            handle_critical_error(session, "Processing account 669", "Error Loading Files", sub_input_folder, to_email)
            return
        
        transaction_summary_df = dataframes['Transaction Summary 669']
        brs_669_df = dataframes['BRS 669']
        afl_gl_interface_staging_data_df = dataframes['AFL_GL_Interface_Staging_Data']
        bank_book_669_df= dataframes['Bank Book 669']
        output_folder =   Path(ConfigConstants.OUTPUT_FOLDER) / ConfigConstants.SUBFOLDER_669
        brs_output_file = output_folder / config_data['brs_669']
        bank_bookkoutput_file= os.path.join(output_folder,config_data['bank_book_669'])
        
        brs_filepath=Path(ConfigConstants.INPUT_FOLDER) / ConfigConstants.SUBFOLDER_669 / config_data['brs_669']
        shutil.copy(brs_filepath,output_folder)
        
        filtered_interface_data = interface_filter(afl_gl_interface_staging_data_df)
        bank_balance = bankbook_report(afl_gl_interface_staging_data_df,bank_book_669_df,output_folder)

        generate_brs_report(transaction_summary_df, brs_669_df, brs_output_file, filtered_interface_data, bank_balance)

        insert_detail_log(session, "Axis Finance Bank Reconciliation Process", "Axis Finance BRS Task", "N/A",
                            'BRS.AutoMail@axisfinance.in', f'N/A', f"Working of Account 669 is done", loglevel="Info")

        upload_file_sftp(([brs_output_file,bank_bookkoutput_file]), "669")
        success_mail(to_email,"Axis Finance BRS",[brs_output_file, bank_bookkoutput_file])

        result = f""" Account 669 have been processed successfully!!
        BRS Output File: {brs_output_file}
        Bank Book Output File: {bank_bookkoutput_file}
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
        error_logger.error(f"Critical error in BRS process: {e}")
        # traceback.print_exc()
        # handle_critical_error(session, "BRS Process Failure", to_email)
        return f"Error in processing BRS for Account - 669: {e}", "Failure"