# app/services/process_service.py

from datetime import datetime

def process_one():
    print("Processing task 1")
    print(datetime.utcnow())
    return "Process one completed successfully.", "Success"


# process_one()