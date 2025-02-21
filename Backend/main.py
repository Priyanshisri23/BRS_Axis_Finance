from init.folder_manager import create_folder_structure
from db.db_operations import insert_detail_log, insert_process_status
from db.models import get_db_engine, get_session
from init.email_service import start_mail, success_mail
from datetime import datetime
# from process import account_7687
# from process import account_9197
# from process import account_669
# from process import account_8350
# from process import account_86033
# from process import account_607
from process import sftp_handler_axis
import sys
import traceback

session = get_session(get_db_engine())
insert_detail_log(session, "Axis Finance Bank Reconciliation Process", "Axis Finance BRS Task", "N/A",
                            'BRS.AutoMail@axisfinance.in', 'N/A', "Process has been started", loglevel="Started")
insert_process_status(session, datetime.now(), "Axis Finance Bank Reconciliation Process",
                            "Axis Finance BRS Task", "N/A", 'BRS.AutoMail@axisfinance.in', "Started", "Process has been started")

print('1============>')
start_mail("Axis Finance BRS")
print('2============>')
try:
    create_folder_structure()
except Exception as e:
        e_type, e_obj, e_tb = sys.exc_info()
        print((str(e_tb.tb_lineno)))
        print('Exception Line Number - {0} , Exception Message - {1}'.format(str(e_tb.tb_lineno),e.__str__()))


try:
    sftp_handler_axis.sftp_hander()
except Exception as e:
        e_type, e_obj, e_tb = sys.exc_info()
        print((str(e_tb.tb_lineno)))
        print('Exception Line Number - {0} , Exception Message - {1}'.format(str(e_tb.tb_lineno),e.__str__()))


try: 
    # account_7687.main()

    # account_9197.main()

    # account_669.main()

#     output_file = account_8350.main()
#     print('OUTPUT FILE---->', output_file)

#     output_file = account_86033.main()
#     output_file = account_607.main()

    insert_detail_log(session, "Axis Finance Bank Reconciliation Process", "Axis Finance BRS Task", "N/A",
                            'BRS.AutoMail@axisfinance.in', 'N/A', "Process has been Successfull", loglevel="Successfull")
    insert_process_status(session, datetime.now(), "Axis Finance Bank Reconciliation Process",
                            "Axis Finance BRS Task", "N/A", 'deepak.soni@ag-technologies.com', "Successfull", "Process has been Successfull")
except Exception as e:
        e_type, e_obj, e_tb = sys.exc_info()
        print((str(e_tb.tb_lineno)))
        print('Exception Line Number - {0} , Exception Message - {1}'.format(str(e_tb.tb_lineno),e.__str__()))

# success_mail("Axis Finance BRS",output_file)
# print('4============>')