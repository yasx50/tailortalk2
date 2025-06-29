from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from ai_agent.ai_integration import compiled_graph
from ai_agent.fetch_calendar import get_all_calendars
from ai_agent.events import get_all_events
import uvicorn
import os



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    result = compiled_graph.invoke({"input": req.message})
    return {"reply": result["output"]}

@app.get("/calendar")
def fetch_calendar():
    return get_all_calendars()

@app.get("/events")
def fetch_calendar():
    return get_all_events()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Use PORT env variable or fallback to 8000
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
