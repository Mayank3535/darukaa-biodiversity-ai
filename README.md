# EcoReason — AI Biodiversity Intelligence Engine

A time-boxed hackathon implementation for the Darukaa.Earth AI Biodiversity Intelligence Chatbot Challenge.

## What it demonstrates
- FastAPI backend
- PostgreSQL + pgvector semantic retrieval
- Gemini embeddings + Gemini 2.5 Flash generation
- LangGraph stateful reasoning workflow
- Structured environmental state extraction
- Clarifying questions for incomplete inputs
- Multi-metric reasoning across soil, climate, land use and biodiversity
- Evidence-backed recommendations with source metadata
- Evaluation scenarios and retrieval/grounding metrics

## Quick start

### 1. Requirements
- Python 3.11+
- Docker Desktop
- VS Code
- A free Gemini API key from Google AI Studio

### 2. Create environment
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure API key
Copy `.env.example` to `.env` and set `GEMINI_API_KEY`.

### 4. Start PostgreSQL + pgvector
```powershell
docker compose up -d db
```

### 5. Initialize the knowledge base
```powershell
python scripts_ingest.py
```

### 6. Run API
```powershell
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs

## Demo request
POST `/analyze` with:
```json
{
  "region": "semi-arid",
  "rainfall": "low",
  "soil": {"organic_carbon": 0.3, "unit": "%"},
  "land_use": {"crop": "wheat", "system": "monoculture"}
}
```

## Important scientific behavior
The system does not invent quantitative effect sizes. If evidence does not support a number, it says the estimate is context-dependent or unavailable.

## Submission
Include this README overview, architecture, database/schema, local setup and CI/CD details in the required Word submission document.
