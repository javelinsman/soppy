"""
schedule assistant using google calendar
"""

from basic.module import Module

from modules.schedule_assistant.google_calendar import GoogleCalendar

import bot_config

class ModuleScheduleAssistant(Module):
    "Module description above"
    def __init__(self):
        super().__init__(__name__)
        self.key = {
            }
        self.calendar = GoogleCalendar()

    def filter(self, message):
        return message["context"]["chat_id"] == bot_config.ADMIN

    def operator(self, message):
        context = message["context"]
        if message["type"] == 'text' and \
           message["data"]["text"] == 'list_from_now':
            self.send_text(context, self.calendar.list_from_now())
