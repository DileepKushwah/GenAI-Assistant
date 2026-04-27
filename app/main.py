from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from modules.config import init_gemini
from modules.memory import ConversationMemory
from modules.pdf_qa import PDFQAEngine
from modules.youtube_summarizer import YouTubeSummarizer
from modules.chatbot import ChatBot

# ── App ───────────────────────────────────────────────────────
app = FastAPI(
    title="GenAI Assistant API",
    description="Multimodal GenAI assistant with RAG, YouTube summarization, and enhanced memory",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Init once at startup ──────────────────────────────────────
model         = init_gemini()
memory        = ConversationMemory()
pdf_engine    = PDFQAEngine(model)
yt_summarizer = YouTubeSummarizer(model)
chatbot       = ChatBot(model, memory)

# ── Request/Response Models ───────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    reply: str
    session_id: str

class YouTubeRequest(BaseModel):
    url: str
    detail_level: str = "Standard"

class PDFQuestionRequest(BaseModel):
    question: str
    session_id: str = "default"

# ── Health ────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "healthy", "version": "2.0.0"}

# ── Chat ──────────────────────────────────────────────────────
@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        reply = chatbot.send(req.message, req.session_id)
        return ChatResponse(reply=reply, session_id=req.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/{session_id}/stats")
def chat_stats(session_id: str):
    try:
        return memory.stats(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/{session_id}/history")
def chat_history(session_id: str):
    try:
        return {
            "history":   memory.get_history(session_id),
            "summaries": memory.get_summaries(session_id),
            "profile":   memory.get_profile(session_id),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/chat/{session_id}/clear")
def clear_chat(session_id: str):
    try:
        memory.clear(session_id)
        return {"status": "cleared", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── PDF ───────────────────────────────────────────────────────
@app.post("/api/pdf/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    try:
        content = await file.read()
        result  = pdf_engine.ingest(content, file.filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pdf/ask")
def ask_pdf(req: PDFQuestionRequest):
    try:
        if pdf_engine.index is None:
            raise HTTPException(
                status_code=400,
                detail="No document indexed. Please upload a PDF first."
            )
        # answer() only takes question — history is inside pdf_engine itself
        answer = pdf_engine.answer(req.question)
        return {"answer": answer}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/pdf/clear")
def clear_pdf():
    try:
        pdf_engine.clear_history()
        return {"status": "pdf chat cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── YouTube ───────────────────────────────────────────────────
@app.post("/api/youtube/summarize")
def summarize_youtube(req: YouTubeRequest):
    try:
        summary = yt_summarizer.summarize(req.url, req.detail_level)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Frontend ──────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")