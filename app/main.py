from typing import Dict, Any

from fastapi import FastAPI

from app.db import init_db
from app.graph import graph
from app.schemas import AnalyzeRequest, ChatRequest

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(
    title="EcoReason — Biodiversity Intelligence Engine",
    version="0.2.0",
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def home():
    return FileResponse("frontend/index.html")

# Simple in-memory conversation store for the hackathon demo.
# This can later be replaced with PostgreSQL/Redis persistence.
sessions: Dict[str, Dict[str, Any]] = {}


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ecoreason",
    }


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    text = req.query or req.model_dump_json(exclude_none=True)

    result = graph.invoke({
        "user_input": text,
        "previous_state": {},
    })

    return result


@app.post("/chat")
def chat(req: ChatRequest):
    session_id = req.session_id

    previous_state = sessions.get(
        session_id,
        {}
    )

    result = graph.invoke({
        "user_input": req.message,
        "previous_state": previous_state,
    })

    environmental_state = result.get(
        "environmental_state",
        previous_state,
    )

    sessions[session_id] = environmental_state

    return result