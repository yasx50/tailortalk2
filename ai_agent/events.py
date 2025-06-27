
import datetime
from ai_agent.calendar_setup import get_calendar_service


def get_all_events():
    service = get_calendar_service()
    if not service:
        return {"error": "❌ Calendar service unavailable."}

    try:
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        one_year_later = (datetime.datetime.utcnow() + datetime.timedelta(days=365)).isoformat() + 'Z'

        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=one_year_later,
            maxResults=2500,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        return events

    except Exception as e:
        return {"error": f"❌ Could not fetch calendar: {str(e)}"}
