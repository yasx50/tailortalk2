import os
import re
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import dateparser
from datetime import datetime, timedelta
from ai_agent.calendar_setup import get_free_slots, book_slot
from typing import TypedDict
from ai_agent.intent_detect import detect_intent
load_dotenv()

api_key = os.getenv("API_KEY")
llm = ChatGroq(api_key=api_key, model_name="llama3-70b-8192")

# 🔥 Powerful System Prompt
system_prompt = """
You are a smart, friendly AI assistant that :
- Book appointments on their Google Calendar
- View their schedule
- Answer general questions

You can:
- Understand natural language like "tomorrow 3pm", "next Monday"
- Reply to queries like "What day is today?" or "Who are you?"
- Be polite, helpful, and context-aware
"""


# ✅ Extract person's name from message
def extract_person_name(message):
    match = re.search(r"with (.+)", message)
    if match:
        return match.group(1).strip().title()
    return "Unnamed Person"

# ✅ Main message processor
def process_message(state):
    message = state["input"]
    intent = detect_intent(message)
    dt = dateparser.parse(message)

    # 👉 Book meeting if intent is booking
    if intent == "book" and dt:
        existing_events = get_free_slots(dt.date())
        if existing_events:
            return {
                "input": message,
                "output": f"📅 You already have events around {dt.strftime('%I:%M %p, %A')}. Try another time?"
            }

        end_dt = dt + timedelta(minutes=30)
        person = extract_person_name(message)
        event = book_slot(dt, end_dt, summary=f"Meeting with {person}")
        return {
            "input": message,
            "output": f"✅ Booked '{event['summary']}' on {dt.strftime('%A, %d %B %Y at %I:%M %p')}"
        }

    # 👉 Fetch today’s meetings
    elif intent == "fetch":
        today = datetime.now().date()
        events = get_free_slots(today)
        if not events:
            return {"input": message, "output": "📭 No meetings found for today."}
        
        reply = "📅 Your meetings for today:\n"
        for event in events:
            summary = event.get('summary', 'No Title')
            time = event['start'].get('dateTime', event['start'].get('date'))
            reply += f"• {summary} at {time}\n"

        return {"input": message, "output": reply}

    # 👉 Fallback to LLM for general questions
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=message)
    ]
    response = llm.invoke(messages)
    return {
        "input": message,
        "output": response.content
    }

# ✅ LangGraph setup
class ChatState(TypedDict):
    input: str
    output: str

graph = StateGraph(ChatState)
graph.add_node("process", process_message)
graph.set_entry_point("process")
graph.set_finish_point("process")
compiled_graph = graph.compile()
