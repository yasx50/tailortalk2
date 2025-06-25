from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
import dateparser
import os

def get_calendar_service():
    creds = Credentials.from_authorized_user_file("token.json")
    return build('calendar', 'v3', credentials=creds)

def get_free_slots(date):
    service = get_calendar_service()
    start = datetime.datetime.combine(date, datetime.time.min).isoformat() + 'Z'
    end = datetime.datetime.combine(date, datetime.time.max).isoformat() + 'Z'
    events = service.events().list(calendarId='primary', timeMin=start, timeMax=end).execute()
    return events.get('items', [])

def book_slot(start_dt, end_dt, summary="Meeting with user"):
    service = get_calendar_service()
    event = {
        'summary': summary,
        'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Asia/Kolkata'}
    }
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return created_event
