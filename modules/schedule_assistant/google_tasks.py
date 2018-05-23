"""
manages google calendar
"""

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime
import re

import bot_config
import dateutil.parser

class GoogleTasks:
    def __init__(self):
        scopes = 'https://www.googleapis.com/auth/tasks'
        store = file.Storage('modules/schedule_assistant/credentials_tasks.json')
        creds = store.get()
        print(store, creds)
        if not creds or creds.invalid:
            raise Exception("Google Tasks Authentication Error")
        self.service = build('tasks', 'v1', http=creds.authorize(Http()))

    def tasklists(self):
        results = self.service.tasklist().list(maxResults=10).execute()
        items = results.get('items', [])
        return [(item['title'], item['id']) for item in items]

    def tasks(self):
        tasks = self.service.tasks().list(tasklist='MTU4NjIwMTg2ODc0OTYzOTY3Nzk6NjgxODIwMDk4MTUyMDIxNzow').execute()
        lst = []
        for task in tasks['items']:
            title = task['title']
            status = task['status']
            duedate = task['due'] if 'due' in task else None
            notes = task['notes'] if 'notes' in task else ''

            lst.append({
                'title': title,
                'status': status,
                'due': self.handle_due(duedate, *self.parse_duetime(notes)),
                'duration': self.parse_duration(notes),
                'repetition': self.parse_repetition(notes),
            })
        return lst

    def handle_due(self, duedate, due_hour, due_minute):
        if duedate is None:
            due = datetime.datetime.now() + datetime.timedelta(30)
        else:
            due = dateutil.parser.parse(duedate) + datetime.timedelta(0, due_hour * 3600 + due_minute * 60)
        return due

    def parse_duetime(self, text):
        pat = re.compile('[^\d(?:오전|오후)]*(?:\d+[^\d\s]+\s*)*\s*(오전|오후)?\s*(\d+)시\s*(반)?\s*까지.*')
        mat = pat.match(text)
        if mat is None:
            return 23, 59
        else:
            hour = int(mat.group(2))
            minute = 0 if mat.group(3) is None else 30
            if mat.group(1) == '오전' and hour == 12:
                hour = 0
            if mat.group(1) == '오후' and hour != 12:
                hour += 12
            return hour, minute

    def parse_repetition(self, text):
        pat = re.compile('(?:\d*[^\d]+)*\s*(\d+)번.*')
        mat = pat.match(text)
        if mat is None:
            return 1
        else:
            return int(mat.group(1))

    def parse_duration(self, text):
        pat = re.compile('(?:\d*[^\d]+)*\s*(\d+)시간\s*(반)?.*')
        mat = pat.match(text)
        if mat is None:
            return 2
        else:
            ret = int(mat.group(1))
            if mat.group(2) is not None:
                ret += 0.5
            return ret


if __name__ == "__main__":
    print(GoogleTasks().tasks())
