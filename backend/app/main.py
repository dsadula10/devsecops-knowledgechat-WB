from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from typing import Optional
import uuid
import json
import os
import uvicorn

from app.models import ChatRequest
from app.agent import DevSecOpsAgent
from app.database import init_db

app = FastAPI(title="DevSecOps Assistant API")

origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = DevSecOpsAgent()

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/")
async def health():
    return {"status": "healthy"}

@app.get("/tools")
async def get_tools():
    return {"tools": agent.get_tool_definitions()}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    async def stream_generator():
        try:
            async for event in agent.chat_stream(request.message, conversation_id):
                data = {
                    "type": event.type,
                    "conversation_id": conversation_id,
                    "content": event.content,
                    "tool": event.tool,
                    "args": event.args,
                    "result": event.result
                }
                # Filter None values to keep payload clean
                yield {"data": json.dumps({k: v for k, v in data.items() if v is not None})}
        except Exception as e:
            yield {"data": json.dumps({"type": "error", "content": str(e)})}

    return EventSourceResponse(stream_generator())

@app.get("/projects")
async def list_projects():
    return {"projects": agent.scanner_tool.list_projects()}

@app.get("/tickets")
async def list_tickets(project_id: Optional[str] = None, status: Optional[str] = None):
    tickets = agent.ticket_tool.list_tickets(project_id=project_id, status=status)
    return {"tickets": [t.dict() for t in tickets]}

if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
