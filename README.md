# Darukaa Earth — Biodiversity Intelligence Engine

A hackathon implementation for the Darukaa.Earth AI Biodiversity Intelligence Chatbot Challenge — an AI environmental scientist, not a chatbot.

## What it demonstrates
- A conversational web UI — describe your land/farm situation in plain text, no JSON required
- FastAPI backend served at the root
- PostgreSQL + pgvector semantic retrieval over a curated scientific corpus (FAO, IPCC, ESA WorldCover)
- Gemini embeddings (`gemini-embedding-001`) + Gemini generation (`gemini-3.5-flash`)
- LangGraph stateful reasoning workflow (parse → validate → clarify/retrieve → reason)
- Structured environmental state extraction from free-text input
- Clarifying questions when critical inputs are missing
- Multi-metric reasoning across soil, climate, land use and biodiversity
- Evidence-backed recommendations with source titles, organizations and URLs
- Retry/backoff handling for transient LLM provider errors

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
Copy `.env.example` to `.env` and set:
```text
GEMINI_API_KEY=<your_key>
GENERATION_MODEL=gemini-3.5-flash
EMBEDDING_MODEL=gemini-embedding-001
DATABASE_URL=postgresql://ecoreason:ecoreason@localhost:5433/ecoreason
```

### 4. Start PostgreSQL + pgvector
```powershell
docker compose up -d db
```

### 5. Initialize the database and knowledge base
```powershell
python -c "from app.db import init_db; init_db(); print('DATABASE OK')"
python scripts_ingest.py
```

### 6. Run the API and UI
```powershell
uvicorn app.main:app --reload
```
Open **http://127.0.0.1:8000**.

## Demo

Just type your situation in plain text on the web UI — no JSON needed. For example:

> *"I have a wheat farm in a semi-arid region with low rainfall. Soil organic carbon is 0.3% and it is currently monoculture."*

The system extracts the structured environmental state automatically, retrieves supporting scientific evidence, and returns a full assessment: diagnosis, key variable interactions, recommended intervention, expected effects, implementation steps, monitoring metrics, time horizon, sources, and confidence level.

If information is missing (e.g. you only mention soil carbon), the system asks a clarifying question before reasoning.

### API access (optional)
For programmatic/structured input, `POST /analyze` also accepts JSON directly:
```json
{
  "region": "semi-arid",
  "rainfall": "low",
  "soil": {"organic_carbon": 0.3, "unit": "%"},
  "land_use": {"crop": "wheat", "system": "monoculture"}
}
```
Swagger docs available at **http://127.0.0.1:8000/docs**.

## Important scientific behavior
The system does not invent quantitative effect sizes. If retrieved evidence does not support a specific number, it reports the expected direction of change and notes that the estimate is context-dependent rather than inventing a percentage.
