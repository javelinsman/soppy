"""
manages google calendar
"""

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime
import re

import bot_config

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
            due = task['due'] if 'due' in task else None
            notes = task['notes'] if 'notes' in task else ''
            lst.append({
                'title': title,
                'status': status,
                'duedate': due,
                'duration': self.parse_duration(notes),
                'repetition': self.parse_repetition(notes),
            })
        return lst

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
