# cv2job

Turn your CV into job opportunities: AI-powered job matching based on your resume.

Upload your CV (PDF/DOCX) → an AI model extracts your profile → the app searches
live job boards → each opening is scored against your CV with a short
"why this fits" explanation and a direct link to apply.

## Features

- **CV understanding** — pypdf/python-docx text extraction, then an LLM structures
  it into an editable profile (titles, skills, seniority, experience, languages).
- **Live job search** — aggregates Remotive and Arbeitnow (no keys needed), plus
  Adzuna and JSearch/RapidAPI (free keys) with deduplication across sources.
- **AI match scoring** — jobs are ranked 0–100 against your profile with a short
  explanation per job. A keyword-based fallback keeps the app fully working with
  zero API keys.
- **Switchable AI models** — Gemini (free tier, default), Claude and OpenAI;
  unavailable providers are disabled in the UI automatically.
- **No accounts** — your CV is processed in memory and never stored; search
  history lives in your browser only.

## Architecture

```
frontend/   React + Vite + TypeScript single-page app
backend/    Python FastAPI
            ├── llm/         provider adapters (Gemini / Claude / OpenAI)
            ├── jobsources/  job board adapters + parallel aggregator
            └── services/    extraction, profile, dedupe, matching
```

The two apps share no code and communicate only over the HTTP API
(`/api/...`, proxied by the Vite dev server).

## Getting started

Requirements: Python 3.11+, Node 20+.

### 1. Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # optional: add API keys (see below)
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev                   # http://localhost:5173
```

The app works immediately with **zero API keys** using the keyless job sources
and keyword matching.

### 3. API keys (optional, all free tiers)

Add to `backend/.env` and restart the backend:

| Key | Enables | Where to get it |
|---|---|---|
| `GEMINI_API_KEY` | AI profile extraction + match scoring (default model) | https://aistudio.google.com (free) |
| `ANTHROPIC_API_KEY` | Claude in the model switcher | https://console.anthropic.com |
| `OPENAI_API_KEY` | OpenAI in the model switcher | https://platform.openai.com |
| `ADZUNA_APP_ID` + `ADZUNA_APP_KEY` | Adzuna job listings | https://developer.adzuna.com (free) |
| `RAPIDAPI_KEY` | JSearch (LinkedIn/Indeed/Glassdoor listings) | https://rapidapi.com → subscribe to JSearch (free tier) |

`.env` is git-ignored — never commit real keys.

## API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/health` | Liveness check |
| `GET` | `/api/providers` | Which AI models and job sources are configured |
| `POST` | `/api/cv/parse` | Multipart CV upload → structured profile |
| `POST` | `/api/jobs/match` | Profile → ranked job matches with apply links |

## Tests

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest tests/
```

Covers deduplication, CV text extraction, lexical scoring/pre-filter, and the
LLM JSON-schema normalization.
