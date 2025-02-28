from datetime import datetime
import pytz

class GreetingMessage:

    def __init__(self):
        self.ph_tz = pytz.timezone('Asia/Manila')

    def get_greeting_message(self):
        current_time = datetime.now(self.ph_tz)
        if current_time.hour < 12:
            return "Good morning"
        elif 12 <= current_time.hour < 18:
            return "Good afternoon"
        else:
            return "Good evening"