"""
schedule assistant using google calendar
"""

from basic.module import Module

from modules.schedule_assistant.google_calendar import GoogleCalendar
from modules.schedule_assistant.google_tasks import GoogleTasks
from modules.schedule_assistant.auto_scheduler import AutoScheduler

import bot_config

import datetime
import time
import re

class ModuleScheduleAssistant(Module):
    "Module description above"
    def __init__(self):
        super().__init__(__name__)
        self.key = {
            }
        self.calendar = GoogleCalendar()
        self.tasks = GoogleTasks()
        self.auto_scheduler = AutoScheduler()

    def filter(self, message):
        return all((
            message["context"]["chat_id"] == bot_config.ADMIN,
            message["type"] == 'text'
            ))

    def operator(self, message):
        try:
            context = message["context"]
            text = message["data"]["text"]
            args = text.split()
            if args[0] == '일정목록':
                num = 10
                if len(args) >= 2:
                    num = int(args[1])
                self.send_text(context, self.calendar.list_from_now(num))
            elif args[0] == '과업목록':
                self.send_text(context, str(self.tasks.tasks()))
            elif args[0] == '일정생성':
                m1, d1, h1, m2, d2, h2 = map(int, args[1:7])
                title = text[text.find(':')+2:]
                year = time.localtime().tm_year
                start = datetime.datetime(year, m1, d1, h1, 0, 0)
                end = datetime.datetime(year, m2, d2, h2, 0, 0)
                self.send_text(context, self.calendar.create(title, start, end))
            elif '부터' in text and '까지' in text:
                start_text = text[:text.find('부터')]
                end_text = text[text.find('부터')+2:text.find('까지')]
                title = text[text.find('까지')+2:].strip()
                start = self.parse_datetime_text(start_text)
                end = self.parse_datetime_text(end_text, start)
                print(start)
                print(end)
                self.send_text(context, self.calendar.create(title, start, end))
            elif args[0] in ['스케쥴', '일정']:
                tasks = self.tasks.tasks()
                events = self.calendar.events()
                def send_text(text):
                    self.send_text(context, text)
                timeout = 10
                if len(args) > 1:
                    timeout = int(args[1])
                self.auto_scheduler.schedule(events, tasks, send_text, timeout)
        except Exception as e:
            self.send_text(context, str(e))

    def parse_datetime_text(self, text, before=None):
        try:
            d1 = self.parse_day(text)
        except Exception:
            if before is not None:
                d1 = before
            else:
                raise Exception("datetime parsing error")
        d2 = self.parse_time(text)
        return datetime.datetime(d1.year, d1.month, d1.day, d2.hour, d2.minute, 0)

    def parse_day(self, text):
        relative_indicators = ['오늘', '내일', '모레', '글피']
        wdays = ['월', '화', '수', '목', '금', '토', '일']
        now = datetime.datetime.now()
        for i, relative_indicator in enumerate(relative_indicators):
            if relative_indicator in text:
                return now + datetime.timedelta(i)
        day_offset = 0
        det = False
        for next_week in ['담주', '다음주', '다음 주']:
            if next_week in text:
                day_offset += 7
                break
        for next2_week in ['다담주', '다다음주', '다다음 주']:
            if next2_week in text:
                day_offset += 7
                break
        for i, wday in enumerate(wdays):
            if (wday + '요일') in text or (wday + '욜') in text:
                day_offset += i - now.weekday()
                det = True
        if det:
            print(day_offset)
            return now + datetime.timedelta(day_offset)
        p = re.compile('[^\d]*(\d+)월[^\d]*(\d+)일.*')
        m = p.match(text)
        if m is not None:
            month = int(m.group(1))
            day = int(m.group(2))
            return datetime.datetime(now.year, month, day, 7, 0, 0)
        raise Exception("day parsing error")

    def parse_time(self, text):
        if '일' in text:
            text = text.split('일')[-1]
        p = re.compile('[^\d]*(\d+)시\s*(반?).*')
        m = p.match(text)
        hour = int(m.group(1))
        minute = 0
        if len(m.groups()) > 1 and m.group(2) == '반':
            minute = 30
        if '오전' in text and hour == 12:
            hour = 0
        if '오후' in text and hour != 12:
            hour += 12
        return datetime.datetime(100, 1, 1, hour, minute, 0)
