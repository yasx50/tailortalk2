from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
import pickle

# ✅ Load saved OAuth credentials
def get_calendar_service():
    try:
        with open('token.pkl', 'rb') as token:
            creds = pickle.load(token)
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        print(f"❌ Error loading calendar credentials: {e}")
        return None

# ✅ Get events for a specific date
def get_free_slots(date):
    service = get_calendar_service()
    if not service:
        return []

    start = datetime.datetime.combine(date, datetime.time.min).isoformat() + 'Z'
    end = datetime.datetime.combine(date, datetime.time.max).isoformat() + 'Z'

    try:
        events = service.events().list(
            calendarId='primary',
            timeMin=start,
            timeMax=end,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return events.get('items', [])
    except Exception as e:
        print(f"❌ Error fetching events: {e}")
        return []

# ✅ Book a meeting/event in the calendar
def book_slot(start_dt, end_dt, summary="Meeting with user"):
    service = get_calendar_service()
    if not service:
        return {"summary": "❌ Calendar service unavailable."}

    event = {
        'summary': summary,
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': 'Asia/Kolkata'
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': 'Asia/Kolkata'
        }
    }

    try:
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        return created_event
    except Exception as e:
        print(f"❌ Error booking event: {e}")
        return {"summary": "❌ Failed to book event."}
