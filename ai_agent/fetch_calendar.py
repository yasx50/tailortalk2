from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
import pickle

def get_calendar_service():
    try:
        with open('token.pkl', 'rb') as token:
            creds = pickle.load(token)
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        print(f"❌ Error loading calendar credentials: {e}")
        return None

def get_all_calendars():
    service = get_calendar_service()
    if not service:
        return {"error": "❌ Calendar service unavailable."}

    try:
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        return calendars

    except Exception as e:
        print(f"❌ Error fetching calendars: {e}")
        return {"error": "❌ Could not fetch calendar list."}
