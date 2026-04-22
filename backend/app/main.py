import json
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .agent import Agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

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

    gen = agent.chat(req.session_id, req.message)
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
