import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import dateparser
from datetime import datetime, timedelta
from ai_agent.calendar_setup import get_free_slots, book_slot
from typing import TypedDict

load_dotenv()  

api_key = os.getenv("API_KEY")
llm = ChatGroq(api_key=api_key, model_name="llama3-70b-8192")

# 🔥 Powerful System Prompt
system_prompt = """
You are a smart, friendly AI assistant that  book appointments on their Google Calendar and also gives them list of their appointments whenever they ask .
you have access of google calendar

You should:
- Understand natural language like "tomorrow afternoon" or "next Friday"
- Respond intelligently to general questions like "What's today's date?" or "Are you a bot?"
- Be polite and helpful
- Guide the user toward scheduling if possible
"""

# ✅ Main message handler
def process_message(state):
    message = state["input"]

    # 🔹 System + User messages sent to LLM
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=message)
    ]
    response = llm.invoke(messages)
    ai_reply = response.content

    # 🔹 Try to parse datetime
    dt = dateparser.parse(message)

    if dt:
        # Check for conflicts
        existing_events = get_free_slots(dt.date())
        if existing_events:
            return {
                "input": message,
                "output": f"{ai_reply}\n\n📅 You already have events around {dt.strftime('%I:%M %p, %A')}. Try another time?"
            }

        end_dt = dt + timedelta(minutes=30)
        event = book_slot(dt, end_dt)
        return {
            "input": message,
            "output": f"{ai_reply}\n\n✅ Booked '{event['summary']}' on {dt.strftime('%A, %d %B %Y at %I:%M %p')}"
        }

    # 🔹 If no datetime found, just reply naturally
    return {
        "input": message,
        "output": ai_reply
    }

# ✅ LangGraph state
class ChatState(TypedDict):
    input: str
    output: str

# ✅ Build the graph
graph = StateGraph(ChatState)
graph.add_node("process", process_message)
graph.set_entry_point("process")
graph.set_finish_point("process")
compiled_graph = graph.compile()
