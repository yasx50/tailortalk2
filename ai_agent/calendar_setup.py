import os
import pickle
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz

# Scopes required for calendar access
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    """
    Authenticate and return Google Calendar service object.
    Handles token refresh and initial authentication.
    """
    creds = None
    
    # Load existing token
    if os.path.exists('token.pkl'):
        try:
            with open('token.pkl', 'rb') as token:
                creds = pickle.load(token)
                print("✅ Loaded existing credentials")
        except Exception as e:
            print(f"⚠️ Error loading token.pkl: {e}")
            creds = None
    
    # Check if credentials are valid
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("🔄 Refreshing expired credentials...")
                creds.refresh(Request())
                print("✅ Credentials refreshed successfully")
            except Exception as e:
                print(f"❌ Error refreshing credentials: {e}")
                creds = None
        
        # If still no valid credentials, run OAuth flow
        if not creds:
            if not os.path.exists('credentials.json'):
                print("❌ credentials.json file not found!")
                print("📝 Please download it from Google Cloud Console:")
                print("   1. Go to https://console.cloud.google.com/")
                print("   2. Enable Google Calendar API")
                print("   3. Create OAuth 2.0 credentials")
                print("   4. Download and save as 'credentials.json'")
                return None
            
            try:
                print("🔐 Starting OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                print("✅ Authentication successful")
            except Exception as e:
                print(f"❌ OAuth flow failed: {e}")
                return None
        
        # Save credentials for next run
        try:
            with open('token.pkl', 'wb') as token:
                pickle.dump(creds, token)
                print("✅ Credentials saved to token.pkl")
        except Exception as e:
            print(f"⚠️ Could not save credentials: {e}")
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        # Test the connection
        service.calendarList().list().execute()
        print("✅ Google Calendar service connected successfully")
        return service
    except Exception as e:
        print(f"❌ Failed to build calendar service: {e}")
        return None

def get_calendar_service():
    """Get authenticated calendar service with better error handling."""
    return authenticate_google_calendar()

def test_calendar_connection():
    """Test if calendar connection is working."""
    service = get_calendar_service()
    if not service:
        return False
    
    try:
        # Try to get calendar list
        calendars = service.calendarList().list().execute()
        print(f"✅ Found {len(calendars.get('items', []))} calendars")
        
        # Show primary calendar info
        for calendar in calendars.get('items', []):
            if calendar.get('primary'):
                print(f"📅 Primary calendar: {calendar.get('summary')}")
                break
        
        return True
    except HttpError as e:
        print(f"❌ Calendar API error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def get_events_for_date(date, timezone='Asia/Kolkata'):
    """
    Get all events for a specific date with improved error handling.
    
    Args:
        date: datetime.date object
        timezone: timezone string (default: Asia/Kolkata)
    
    Returns:
        List of events or empty list if error
    """
    service = get_calendar_service()
    if not service:
        print("❌ Calendar service not available")
        return []
    
    try:
        # Set timezone
        tz = pytz.timezone(timezone)
        
        # Create start and end times for the date
        start_dt = tz.localize(datetime.datetime.combine(date, datetime.time.min))
        end_dt = tz.localize(datetime.datetime.combine(date, datetime.time.max))
        
        print(f"🔍 Fetching events for {date} ({timezone})")
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_dt.isoformat(),
            timeMax=end_dt.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"✅ Found {len(events)} events for {date}")
        
        # Print event details for debugging
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"   📋 {event.get('summary', 'No title')}: {start}")
        
        return events
        
    except HttpError as e:
        print(f"❌ Calendar API error: {e}")
        return []
    except Exception as e:
        print(f"❌ Error fetching events: {e}")
        return []

def find_free_slots(date, slot_duration_minutes=60, work_start_hour=9, work_end_hour=17, timezone='Asia/Kolkata'):
    """
    Find free time slots on a given date.
    
    Args:
        date: datetime.date object
        slot_duration_minutes: minimum slot duration in minutes
        work_start_hour: start of work day (24-hour format)
        work_end_hour: end of work day (24-hour format)
        timezone: timezone string
    
    Returns:
        List of free time slots as (start_datetime, end_datetime) tuples
    """
    events = get_events_for_date(date, timezone)
    if events is None:
        return []
    
    tz = pytz.timezone(timezone)
    work_start = tz.localize(datetime.datetime.combine(date, datetime.time(work_start_hour, 0)))
    work_end = tz.localize(datetime.datetime.combine(date, datetime.time(work_end_hour, 0)))
    
    # Get busy periods
    busy_periods = []
    for event in events:
        start_str = event['start'].get('dateTime')
        end_str = event['end'].get('dateTime')
        
        if start_str and end_str:  # Skip all-day events
            start_dt = datetime.datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            end_dt = datetime.datetime.fromisoformat(end_str.replace('Z', '+00:00'))
            
            # Convert to local timezone
            start_dt = start_dt.astimezone(tz)
            end_dt = end_dt.astimezone(tz)
            
            busy_periods.append((start_dt, end_dt))
    
    # Sort busy periods by start time
    busy_periods.sort(key=lambda x: x[0])
    
    # Find free slots
    free_slots = []
    current_time = work_start
    
    for busy_start, busy_end in busy_periods:
        # Check if there's a free slot before this busy period
        if current_time < busy_start:
            slot_duration = busy_start - current_time
            if slot_duration.total_seconds() >= slot_duration_minutes * 60:
                free_slots.append((current_time, busy_start))
        
        # Move current time to end of busy period
        current_time = max(current_time, busy_end)
    
    # Check for free slot after last busy period
    if current_time < work_end:
        slot_duration = work_end - current_time
        if slot_duration.total_seconds() >= slot_duration_minutes * 60:
            free_slots.append((current_time, work_end))
    
    print(f"✅ Found {len(free_slots)} free slots of {slot_duration_minutes}+ minutes")
    for i, (start, end) in enumerate(free_slots, 1):
        duration = (end - start).total_seconds() / 60
        print(f"   🆓 Slot {i}: {start.strftime('%H:%M')} - {end.strftime('%H:%M')} ({duration:.0f} mins)")
    
    return free_slots

def book_meeting(start_datetime, end_datetime, summary="Meeting", description="", timezone='Asia/Kolkata'):
    """
    Book a meeting in the calendar with comprehensive error handling.
    
    Args:
        start_datetime: datetime object for meeting start
        end_datetime: datetime object for meeting end
        summary: meeting title
        description: meeting description
        timezone: timezone string
    
    Returns:
        Dict with success status and event details or error message
    """
    service = get_calendar_service()
    if not service:
        return {
            "success": False,
            "error": "Calendar service not available"
        }
    
    try:
        # Ensure datetimes are timezone-aware
        tz = pytz.timezone(timezone)
        if start_datetime.tzinfo is None:
            start_datetime = tz.localize(start_datetime)
        if end_datetime.tzinfo is None:
            end_datetime = tz.localize(end_datetime)
        
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': timezone,
            },
        }
        
        print(f"📅 Booking meeting: {summary}")
        print(f"   🕐 Start: {start_datetime.strftime('%Y-%m-%d %H:%M %Z')}")
        print(f"   🕐 End: {end_datetime.strftime('%Y-%m-%d %H:%M %Z')}")
        
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        
        return {
            "success": True,
            "event_id": created_event.get('id'),
            "html_link": created_event.get('htmlLink'),
            "summary": summary,
            "start": start_datetime.isoformat(),
            "end": end_datetime.isoformat()
        }
        
    except HttpError as e:
        error_msg = f"Calendar API error: {e}"
        print(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        print(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}

# 🧪 Testing functions
def run_diagnostics():
    """Run comprehensive diagnostics to identify issues."""
    print("🔍 Running Google Calendar diagnostics...\n")
    
    # Check files
    print("1️⃣ Checking required files:")
    files_to_check = ['credentials.json', 'token.pkl']
    for file in files_to_check:
        if os.path.exists(file):
            print(f"   ✅ {file} found")
        else:
            print(f"   ❌ {file} missing")
    print()
    
    # Test connection
    print("2️⃣ Testing calendar connection:")
    if test_calendar_connection():
        print("   ✅ Calendar connection successful\n")
        
        # Test getting today's events
        print("3️⃣ Testing event retrieval:")
        today = datetime.date.today()
        events = get_events_for_date(today)
        print(f"   ✅ Successfully retrieved {len(events)} events for today\n")
        
        # Test finding free slots
        print("4️⃣ Testing free slot detection:")
        free_slots = find_free_slots(today)
        if free_slots:
            print(f"   ✅ Found {len(free_slots)} free slots\n")
        else:
            print("   ℹ️ No free slots found (this might be normal)\n")
        
        print("✅ All tests passed! Your calendar integration is working.")
        return True
    else:
        print("   ❌ Calendar connection failed\n")
        return False

# Example usage
if __name__ == "__main__":
    # Run diagnostics
    run_diagnostics()
    
    # Example: Find free slots for today
    today = datetime.date.today()
    free_slots = find_free_slots(today, slot_duration_minutes=30)
    
    # Example: Book a meeting
    if free_slots:
        start_time = free_slots[0][0]
        end_time = start_time + datetime.timedelta(hours=1)
        result = book_meeting(start_time, end_time, "Test Meeting")
        print(f"Booking result: {result}")