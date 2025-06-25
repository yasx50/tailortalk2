from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import dateparser
from datetime import timedelta
from calendar_setup import get_free_slots, book_slot
import os
from typing import TypedDict
load_dotenv()  

api_key = os.getenv("API_KEY")
llm = ChatGroq(api_key=api_key, model_name="llama3-70b-8192")

def process_message(state):
    message = state["input"]
    dt = dateparser.parse(message)
    if not dt:
        return {"output": "Sorry, I couldn't understand the date/time. Please try again."}

    existing_events = get_free_slots(dt.date())
    if existing_events:
        return {"output": f"You already have events at that time. Try another slot."}
    
    end_dt = dt + timedelta(minutes=30)
    event = book_slot(dt, end_dt)
    return {"output": f"✅ Booked: {event['summary']} on {dt.strftime('%A, %d %B %Y at %I:%M %p')}"}
class ChatState(TypedDict):
    input: str
    output: str
graph = StateGraph(ChatState)
graph.add_node("process", process_message)
graph.set_entry_point("process")
graph.set_finish_point("process")
compiled_graph = graph.compile()