"""
manages google calendar
"""

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime

import bot_config

class GoogleCalendar:
    def __init__(self):
        scopes = 'https://www.googleapis.com/auth/calendar'
        store = file.Storage('credentials.json')
        creds = store.get()
        if not creds or creds.invalid:
            raise Exception("Google Calendar Authentication Error")
        self.service = build('calendar', 'v3', http=creds.authorize(Http()))
    
    def list_from_now(self, max_result=10):
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = self.service.events().list(
            calendarId=bot_config.google_calendar_id,
            timeMin=now,
            maxResults=max_result,
            singleEvents=True,
            orderBy='startTime'
            ).execute()
        events = events_result.get('items', [])
        return '\n'.join(['%s %s' % (str(event['start']['dateTime'][:-9]), str(event['summary'])) for event in events])

    def create(self, title, start, end):
        event = {
            "summary": title,
            "start": {
                "dateTime": start.isoformat(),
                "timeZone": 'Asia/Seoul',
            },
            "end": {
                "dateTime": end.isoformat(),
                "timeZone": 'Asia/Seoul',
            }
        }
        event = self.service.events().insert(
            calendarId=bot_config.google_calendar_id,
            body=event
            ).execute()
        return event["summary"]

if __name__ == "__main__":
    print(GoogleCalendar().list_from_now())
