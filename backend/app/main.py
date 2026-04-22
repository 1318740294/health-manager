import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .agent import Agent

app = FastAPI(title="AI 健康管理对话助手")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = Agent()


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.post("/api/chat")
async def chat(req: ChatRequest):
    from .sse import sse_generator
    print(req.session_id, req.message)
    
    gen = agent.chat(req.session_id, req.message)
    print("gen",gen)
    return StreamingResponse(
        sse_generator(gen),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/health")
async def health():
    import datetime

    return {"status": "ok", "timestamp": datetime.datetime.utcnow().isoformat() + "Z"}
