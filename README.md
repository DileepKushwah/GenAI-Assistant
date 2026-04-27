# 🤖 GenAI Assistant

> **RAG-powered multimodal AI assistant** — FastAPI backend · FAISS vector search · Gemini LLM · Docker + Nginx · GitHub Actions CI/CD

[![Build & Deploy](https://github.com/DileepKushwah/GenAI-Assistant/actions/workflows/deploy.yml/badge.svg)](https://github.com/DileepKushwah/GenAI-Assistant/actions/workflows/deploy.yml)

---

## 🎯 Project Goal

Production-grade Generative AI assistant that demonstrates:

- **RAG pipeline** — PDF upload → FAISS vector index → grounded Gemini answers
- **Multimodal inputs** — text chat, PDF Q&A, YouTube video summarization
- **Memory-aware conversations** — sliding window + summary compression
- **Containerized deployment** — Docker + Nginx reverse proxy
- **Automated CI/CD** — GitHub Actions builds & pushes image to GHCR, deploys via SSH

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 💬 **Chat** | Multi-turn conversation with session-aware memory |
| 📄 **PDF RAG Q&A** | Upload PDF → chunk → embed → FAISS → Gemini grounded answer |
| ▶️ **YouTube Summarizer** | Paste URL → transcript → map-reduce summary (Brief / Standard / Detailed) |
| 🧠 **Enhanced Memory** | Sliding window + LLM-compressed summaries + user profile extraction |
| 🔒 **Secure API Key** | Key lives in `.env` on server only — never in source code or image |
| 🐳 **Docker** | Single-command spin-up via `docker compose up` |
| ⚙️ **GitHub Actions** | Auto-build → push GHCR → SSH deploy on every push to `main` |

---

## 🗂️ Project Structure

```
GenAI-Assistant/
│
├── app/                          # FastAPI application (Docker context)
│   ├── Dockerfile
│   ├── main.py                   # FastAPI routes (chat, PDF, YouTube, health)
│   ├── requirements.txt
│   ├── .env                      # ⚠️  NOT committed — holds GEMINI_API_KEY
│   │
│   ├── modules/                  # Core business logic
│   │   ├── config.py             # Gemini init, constants (CHUNK_SIZE, TOP_K, etc.)
│   │   ├── memory.py             # ConversationMemory — history + summaries + profile
│   │   ├── chatbot.py            # ChatBot — wraps memory + model
│   │   ├── pdf_qa.py             # PDFQAEngine — ingest → FAISS → RAG answer
│   │   ├── youtube_summarizer.py # YouTubeSummarizer — transcript + map-reduce
│   │   └── voice_input.py        # (future) microphone → text
│   │
│   └── static/                   # Frontend (HTML/CSS/JS served by FastAPI)
│
├── nginx/
│   └── nginx.conf                # Reverse proxy: port 80 → FastAPI :8000
│
├── .github/
│   └── workflows/
│       └── deploy.yml            # CI/CD: build → GHCR push → SSH deploy
│
├── docker-compose.yml            # Orchestrates api + nginx services
├── .gitignore
├── LICENSE
└── README.md
```

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.10+
- Docker & Docker Compose (for containerized run)
- Gemini API key → [Google AI Studio](https://aistudio.google.com/app/apikey)

### 1. Clone
```bash
git clone https://github.com/DileepKushwah/GenAI-Assistant.git
cd GenAI-Assistant
```

### 2. Create `app/.env`
```bash
# app/.env  — never commit this file
GEMINI_API_KEY=your_key_here
```

> The key is read via `python-dotenv` at startup. It is **not** a runtime variable — it's baked into `.env` and gitignored.

### 3a. Run locally (Python)
```bash
cd app
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Open → http://localhost:8000

### 3b. Run with Docker Compose
```bash
# from repo root
docker compose up --build
```
- API → http://localhost/api/
- UI  → http://localhost/

---

<<<<<<< HEAD
## 🏗️ Architecture
=======
## 🚀 Deploy on Streamlit Cloud (Free)

1. Push your project to a **public GitHub repo**
2. Go to → [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"** → select your repo → set `main.py` as entry point
4. Under **"Advanced settings → Secrets"**, add:
   ```toml
   GEMINI_API_KEY = "your_key_here"
   ```
5. Click **Deploy** — live in ~2 minutes 

> The app reads `GEMINI_API_KEY` from environment variables, so Streamlit Secrets work automatically.

---

## Technical Architecture
>>>>>>> c2b5842691f39093114ebaf5d59c68d7d19b3d9e

```
                    ┌─────────────────────────────┐
                    │        Client (Browser)       │
                    │  Text / PDF upload / YouTube  │
                    └──────────────┬───────────────┘
                                   │ HTTP :80
                    ┌──────────────▼───────────────┐
                    │         Nginx :80             │
                    │    Reverse Proxy + Static     │
                    └──────────────┬───────────────┘
                                   │ proxy_pass :8000
                    ┌──────────────▼───────────────┐
                    │       FastAPI (uvicorn)        │
                    │         main.py               │
                    └───┬──────────┬──────────┬────┘
                        │          │          │
              ┌─────────▼──┐  ┌────▼────┐  ┌─▼──────────────┐
              │  ChatBot   │  │ PDFQAEng│  │YouTubeSummarizer│
              │ + Memory   │  │  FAISS  │  │ map-reduce      │
              └─────┬──────┘  └────┬────┘  └────────┬────────┘
                    │              │                 │
              ┌─────▼──────────────▼─────────────────▼────────┐
              │              Gemini API (Google)               │
              │    gemini-1.5-flash  |  gemini-embedding-001   │
              └────────────────────────────────────────────────┘
```

### RAG Pipeline (PDF Q&A)

```
PDF bytes
  → PyPDF2 extract text
  → overlapping chunks (1000 chars, 200 overlap)
  → gemini-embedding-001 → float32 vectors
  → FAISS IndexFlatL2
  → query embed → top-4 nearest chunks
  → prompt [context + history] → Gemini → grounded answer
```

### Memory System

```
Each session:
  _store     — full message list [{role, content, time}]
  _summaries — LLM-compressed older turns
  _profiles  — extracted user facts (name, language, interests)

Compression trigger: >20 turns OR >8000 chars
  Oldest N/2 turns → Gemini summary → appended to _summaries
  Recent N turns kept in _store
```

---

## 🚀 CI/CD — GitHub Actions

Workflow: `.github/workflows/deploy.yml`

```
push to main
  │
  ├── Job: build-and-push
  │     checkout → login GHCR → extract metadata
  │     → docker buildx build (./app context)
  │     → push ghcr.io/<owner>/genai-assistant:latest
  │     → push ghcr.io/<owner>/genai-assistant:sha-<commit>
  │
  └── Job: deploy (only on push, not PR)
        SSH into server → git pull → docker pull
        → docker compose down → docker compose up -d
        → docker image prune
```

### Required GitHub Secrets

> **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
|--------|-------|
| `DEPLOY_HOST` | Server IP or hostname |
| `DEPLOY_USER` | SSH username (e.g. `ubuntu`) |
| `DEPLOY_SSH_KEY` | Private SSH key (paste full key including header) |
| `DEPLOY_PATH` | Absolute path on server (e.g. `/opt/genai-assistant`) |
| `DEPLOY_PORT` | SSH port — optional, defaults to `22` |

> `GEMINI_API_KEY` lives in `.env` on the **server only**. It must never be a GitHub Secret or baked into the Docker image.

### Server one-time setup
```bash
# On the server
mkdir -p /opt/genai-assistant
cd /opt/genai-assistant
git clone https://github.com/DileepKushwah/GenAI-Assistant.git .
echo "GEMINI_API_KEY=your_key_here" > app/.env
docker compose up -d
```

---

## 🛠️ Tech Stack

<<<<<<< HEAD
| Layer | Technology |
|-------|-----------|
| **LLM** | Google Gemini 1.5 Flash |
| **Embeddings** | Gemini `embedding-001` |
| **Vector Store** | FAISS (CPU, IndexFlatL2) |
| **PDF Parsing** | PyPDF2 |
| **YouTube** | `youtube-transcript-api` + `yt-dlp` fallback |
| **API** | FastAPI + Uvicorn |
| **Frontend** | Static HTML/CSS/JS (served by FastAPI StaticFiles) |
| **Proxy** | Nginx 1.25-alpine |
| **Container** | Docker + Docker Compose v3.9 |
| **CI/CD** | GitHub Actions → GHCR → SSH deploy |
| **Env** | `python-dotenv` — key in `.env`, gitignored |

---

## 🐛 Known Issues & Planned Fixes

See [`PLANS.md`](./PLANS.md) for detailed roadmap.

### Bugs / Discrepancies (to fix)

| # | Issue | Severity | Plan |
|---|-------|----------|------|
| 1 | `config.py` uses `gemini-3-flash-preview` — invalid model name | ✅ Done | Fixed to `gemini-1.5-flash-latest` (still investigating 404 in v1beta) |
| 2 | Root `app.py` + `requirements.txt` + `modules/` + `utils/` are dead code | ✅ Done | Archived to `legacy/` |
| 3 | `chat_history.csv` in root — runtime file committed | ✅ Done | Gitignored and removed from cache |
| 4 | `app/.env` has hardcoded API key — not gitignored | ✅ Done | Fixed |
| 5 | `app/venv/` committed / present | ✅ Done | Fixed |
| 6 | `deploy.yml` was empty — no CI/CD | ✅ Done | Implemented |
| 7 | `README.md` had git merge conflict markers | ✅ Done | Fixed |
| 8 | `docker-compose.yml` environment variable mismatch | ✅ Done | Fixed with `env_file` |
| 9 | `SpeechRecognition` in `app/requirements.txt` | ✅ Done | Removed |
| 10 | Model 404 Error: `models/gemini-1.5-flash-latest` not found | 🔴 High | **NEW**: Functional test failed. SDK `v1beta` reports model not found. Need to verify correct model name or SDK version. |
=======
- **LLM**: Google Gemini 3 Flash (fast, free-tier available)
- **Embeddings**: Gemini `embedding-001`
- **Vector Store**: FAISS (CPU)
- **PDF Parsing**: PyPDF2
- **YouTube Transcripts**: `youtube-transcript-api`
- **Voice**: `SpeechRecognition` + `pyaudio`
- **Frontend**: Streamlit
- **Env management**: `python-dotenv`
>>>>>>> c2b5842691f39093114ebaf5d59c68d7d19b3d9e

---

## 📄 License
MIT
<<<<<<< HEAD
=======
=======
Purpose of This Project
This project was designed to simulate a real-world Generative AI system by combining multiple AI capabilities into one production-ready assistant. It demonstrates how LLMs can be integrated with multimodal inputs, memory optimization, and secure cloud deployment to build scalable AI applications.

Multimodal GenAI Assistant

A ChatGPT-style **Multimodal Generative AI Assistant** built using Streamlit and Gemini LLM.  
This project integrates conversational AI, document-based Q&A, and YouTube video summarization into a single intelligent interface with memory optimization and secure API deployment.

Project Overview

Multimodal GenAI Assistant is designed to simulate a real-world AI product architecture.  
It supports multiple input types such as text, voice, PDF documents, and video links while maintaining conversational memory and optimized token usage.

Unlike traditional chatbots, this system combines multiple AI workflows into a unified LLM-driven pipeline.

Key Features

💬 ChatGPT-style conversational interface
📄 Document Chat (RAG-style PDF Q&A)
🎥 YouTube Video Summarization
🎤 Voice Input & Text-to-Speech
🧠 Memory Optimization with Summary Storage
🔒 Secure API Key Handling (Streamlit Secrets)
🎨 Custom AI Interface (Not default Streamlit UI)



 🚀 What Makes This Project Unique

✔ Centralized LLM Brain controlling multiple AI tools  
✔ Multimodal interaction (text + voice + document + video)  
✔ Token-efficient summarized memory system  
✔ Production-style modular architecture  
✔ Secure deployment without exposing API keys  

Most beginner projects only implement chat — this system demonstrates **real GenAI engineering workflows**.

---

## 🧠 Architecture Overview

                ┌─────────────────────┐
                │       User Input     │
                │ Text / Voice / PDF   │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Streamlit UI       │
                │ ChatGPT-style Input  │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Chat Controller    │
                │ (modules/chatbot)    │
                └──────────┬──────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   Document Mode      Video Mode        Chat Mode
     (PDF RAG)        (Transcript)       (Memory)

                           │
                           ▼
                ┌─────────────────────┐
                │   utils/llm.py       │
                │  Gemini API Brain    │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Gemini LLM API     │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │  Response to UI      │
                └─────────────────────┘


GenAI-Assistant/
│
├── app.py
├── requirements.txt
│
├── modules/
│ └── chatbot.py
│
└── utils/
├── llm.py
└── summary_memory.py


deployment: https://multigenai.streamlit.app/
>>>>>>> f04cdbf53083f166b66f2c5579f5f90eb9050980
>>>>>>> c2b5842691f39093114ebaf5d59c68d7d19b3d9e
