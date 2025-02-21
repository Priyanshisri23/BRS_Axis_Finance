import os
import socket
import traceback
from datetime import datetime, time
import psutil
import pandas as pd
from sqlalchemy import exc
from app.models.process_data import ProcessData
from app.models.mail_log import MailLog
# from src.utils.custom_logger import error_logger, general_logger
import pandas as pd
from datetime import datetime, time
from sqlalchemy.exc import SQLAlchemyError
import numpy as np
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc


def get_new_processid(session, taskname, process_date):
    """
    Fetch the latest ProcessID for a given task and generate a new one.
    :param session: SQLAlchemy session for database interaction.
    :param taskname: Name of the task.
    :param process_date: Date for which the ProcessID should be generated.
    :return: New ProcessID string.
    """
    try:
        # date_part_filter = process_date.strftime('%Y%m%d')
        date_part_filter = process_date.strftime('%Y%m%d')
        # last_entry = session.query(ProcessData).filter(ProcessData.TaskName == taskname,ProcessData.ProcessID.like(f"{date_part_filter}%")).order_by(ProcessData.ProcessID.desc()).first()
        last_entry = session.query(ProcessData).filter(ProcessData.ProcessID.like(f"{date_part_filter}%")).order_by(ProcessData.ProcessID.desc()).first()

        if last_entry:
            last_processid = str(last_entry.ProcessID)
            date_part, num_part = last_processid[:-3], last_processid[-3:]
            # if date_part == process_date.strftime('%Y%m%d'):
            if date_part == process_date.strftime('%Y%m%d'):
                new_num_part = str(int(num_part) + 1).zfill(3)
                return f"{date_part}{new_num_part}"
        # return f"{process_date.strftime('%Y%m%d')}001"
        return f"{process_date.strftime('%Y%m%d')}001"
    except Exception as e:
        # error_logger.error("Error in get_new_processid: %s. Traceback: %s", e, traceback.format_exc())
        raise


def get_new_runid(session, taskname, process_date):
    """
    Fetch the latest RunID for a given task and increment it if necessary.
    :param session: SQLAlchemy session for database interaction.
    :param taskname: Name of the task.
    :param process_date: Date for which the RunID should be generated.
    :return: New RunID integer.
    """
    try:
        # date_part_filter = process_date.strftime('%Y%m%d')
        date_part_filter = process_date.strftime('%Y%m%d')
        last_entry = session.query(ProcessData).filter(ProcessData.TaskName == taskname,ProcessData.ProcessID.like(f"{date_part_filter}%")).order_by(ProcessData.ProcessID.desc()).first()

        if last_entry:
            last_runid = int(last_entry.RunID)
            processid_str = str(last_entry.ProcessID)
            date_part = processid_str[:-3]
            # if date_part == process_date.strftime('%Y%m%d'):
            if date_part == process_date.strftime('%Y%m%d'):
                return last_runid + 1
        return 1
    except Exception as e:
        # error_logger.error("Error in get_new_runid: %s. Traceback: %s", e, traceback.format_exc())
        raise


def insert_process_status(session, bot_end_time, processname, taskname, app_name,
                          login_user, status, description):
    """
    Insert the status of a process in the ProcessData table.
    :param session: SQLAlchemy session for database interaction.
    :param bot_end_time: End time of the bot process.
    :param processname: Name of the process.
    :param taskname: Task name associated with the process.
    :param app_name: Name of the application.
    :param login_user: ID of the user who logged in.
    :param status: Status of the process ('Started', 'Completed', etc.).
    :param description: Description of the process.
    """
    current_date = datetime.now()
    try:
        if status == 'Started':
            processid = get_new_processid(session, taskname, current_date)
            runid = get_new_runid(session, taskname, current_date)

            new_entry = ProcessData(
                BotStart_Time=datetime.now(),
                BotEnd_Time=bot_end_time,
                ProcessName=processname,
                TaskName=taskname,
                ApplicationName=app_name,
                LoginUserID=login_user,
                Status=status,
                Description=description,
                RunID=runid,
                ProcessID=processid,
            )
            session.add(new_entry)
            session.commit()
            # general_logger.info("Process status inserted: ProcessID %s", processid)
            return new_entry
        existing_entry = session.query(ProcessData).filter(ProcessData.TaskName == taskname,ProcessData.ProcessID.like(f"{current_date.strftime('%Y%m%d')}%")).order_by(ProcessData.ProcessID.desc()).first()
        print(f"Session from DB Operation: {session}")
        print(f"DB Operation: Existing Entry: {existing_entry}")
        if existing_entry:
            existing_entry.BotEnd_Time = bot_end_time
            existing_entry.Status = status
            existing_entry.Description = description
            session.commit()
            # general_logger.info("Process status updated: ProcessID %s", existing_entry.ProcessID)
            return existing_entry
    except exc.SQLAlchemyError as e:
        session.rollback()
        # error_logger.error("Database error in insert_process_status: %s. Traceback: %s", e, traceback.format_exc())
        raise
    except Exception as e:
        # error_logger.error("Error in insert_process_status: %s. Traceback: %s", e, traceback.format_exc())
        raise


"""Run ID And Process ID for the Detaild Logs"""
def get_new_processid_for_detailed_log(session, taskname, current_date):
    try:
        date_part_filter = current_date.strftime('%Y%m%d')
        # last_entry = session.query(MailLog).filter(MailLog.TaskName == taskname, MailLog.ProcessID.like(f"{date_part_filter}%")).order_by(MailLog.ProcessID.desc()).first()
        last_entry = session.query(MailLog).filter(MailLog.ProcessID.like(f"{date_part_filter}%")).order_by(MailLog.ProcessID.desc()).first()
        print('137', last_entry)

        if last_entry:
            last_processid = str(last_entry.ProcessID)
            print('141', last_processid)
            date_part, num_part = last_processid[:-3], last_processid[-3:]
            if date_part == current_date.strftime('%Y%m%d'):
                print('144', date_part)
                new_num_part = str(int(num_part) + 1).zfill(3)
                return f"{date_part}{new_num_part}"
        return f"{current_date.strftime('%Y%m%d')}001"
    except Exception as e:
        # error_logger.error(f"Error in get_new_mail_processid: {e}")
        raise


def get_new_runid_for_detailed_log(session, taskname, current_date):
    try:
        date_part_filter = current_date.strftime('%Y%m%d')
        last_entry = session.query(MailLog).filter(MailLog.TaskName == taskname, MailLog.ProcessID.like(f"{date_part_filter}%")).order_by(MailLog.ProcessID.desc()).first()
        if last_entry:
            last_runid = int(last_entry.RunID)
            processid_str = str(last_entry.ProcessID)
            date_part = processid_str[:-3]
            if date_part == current_date.strftime('%Y%m%d'):
                return last_runid + 1
        return 1
    except Exception as e:
        # error_logger.error(f"Error in get_new_mail_runid: {e}")
        raise

def insert_detail_log(session, processname, taskname, app_name, login_user,
                      recorder_id, description, loglevel):
    """
    Insert detailed information into the MailLog table.
    :param session: SQLAlchemy session for database interaction.
    :param processname: Name of the process.
    :param taskname: Task name associated with the process.
    :param app_name: Name of the application.
    :param login_user: ID of the user who logged in.
    :param recorder_id: Recorder identifier for the entry.
    :param description: Description of the process or event.
    :param loglevel: Log level (e.g., 'Started', 'Error', etc.).
    """
    current_date = datetime.now()
    try:
        processid = get_new_processid_for_detailed_log(session, taskname, current_date)
        # processid = get_new_processid(session, taskname, current_date)
        runid = get_new_runid_for_detailed_log(session, taskname, current_date)

        if loglevel != 'Started':
            existing_entry = session.query(MailLog).filter(MailLog.TaskName == taskname, MailLog.ProcessID.like(f"{current_date.strftime('%Y%m%d')}%")).order_by(MailLog.ProcessID.desc()).first()

            if existing_entry and str(existing_entry.ProcessID)[:-3] == current_date.strftime('%Y%m%d'):
                processid = existing_entry.ProcessID
                runid = existing_entry.RunID

        timestamp = datetime.now()
        system_username = os.getlogin()
        machine_name = socket.gethostname()
        cpu_usage = int(psutil.cpu_percent(interval=1))
        ram_usage = psutil.virtual_memory().used // (1024 * 1024)

        new_entry = MailLog(
            Timestamp=timestamp,
            RunID=runid,
            SystemUsername=system_username,
            MachineName=machine_name,
            ProcessName=processname,
            TaskName=taskname,
            ApplicationName=app_name,
            LoginUserID=login_user,
            RecorderIdentifier=recorder_id,
            Description=description,
            LogLevel=loglevel,
            cpuusage_percentage=cpu_usage,
            ramusage_mb=ram_usage,
            ProcessID=processid,
        )
        session.add(new_entry)
        session.commit()
        # general_logger.info("Detail log inserted: ProcessID %s", processid)
        return new_entry
    except exc.SQLAlchemyError as e:
        session.rollback()
        # error_logger.error("Database error in insert_detail_log: %s. Traceback: %s", e, traceback.format_exc())
        raise
    except Exception as e:
        # error_logger.error("Error in insert_detail_log: %s. Traceback: %s", e, traceback.format_exc())
        raise

