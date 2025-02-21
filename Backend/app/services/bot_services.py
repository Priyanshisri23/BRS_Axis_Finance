# app/services/bot_services.py
import time
import random

class BotService:

    @staticmethod
    def run_bot1():
        try:
            for i in range(10):
                time.sleep(1)
                print(f"Bot 1: {i}")
            # Simulate success or failure
            if random.choice([True, False]):
                return "Bot 1 process executed successfully.", "Success"
            else:
                raise Exception("Bot 1 failed due to an unexpected error.")
        except Exception as e:
            return str(e), "Failure"

    @staticmethod
    def run_bot2():
        try:
            # Simulate some process
            time.sleep(5)
            if random.choice([True, False]):
                return "Bot 2 process executed successfully.", "Success"
            else:
                raise Exception("Bot 2 encountered a failure.")
        except Exception as e:
            return str(e), "Failure"

    @staticmethod
    def run_bot3():
        try:
            # Simulate some process
            time.sleep(3)
            if random.choice([True, False]):
                return "Bot 3 process executed successfully.", "Success"
            else:
                raise Exception("Bot 3 encountered an exception.")
        except Exception as e:
            return str(e), "Failure"

    @staticmethod
    def run_bot4():
        try:
            # Simulate some process
            time.sleep(7)
            if random.choice([True, False]):
                return "Bot 4 process executed successfully.", "Success"
            else:
                raise Exception("Bot 4 failed due to process error.")
        except Exception as e:
            return str(e), "Failure"
