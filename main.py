from fastapi import FastAPI
from pydantic import BaseModel
from ai_integration import compiled_graph

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    result = compiled_graph.invoke({"input": req.message})
    return {"reply": result["output"]}
