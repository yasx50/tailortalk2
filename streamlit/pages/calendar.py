import streamlit as st
from streamlit_calendar import calendar
import requests

st.set_page_config(layout="wide")
st.title("📅 Google Calendar View")

# Fetch events from your FastAPI backend
res = requests.get("http://localhost:8000/events")
data = res.json()

if "error" in data:
    st.error(data["error"])
else:
    # Convert events to FullCalendar format
    events = []
    for event in data:
        start = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date")
        end = event.get("end", {}).get("dateTime") or event.get("end", {}).get("date")
        summary = event.get("summary", "No Title")

        events.append({
            "title": summary,
            "start": start,
            "end": end
        })

    calendar_options = {
        "initialView": "dayGridMonth",  # month / timeGridWeek / timeGridDay
        "editable": False,
        "selectable": True,
        "height": "auto"
    }

    calendar(events=events, options=calendar_options)
