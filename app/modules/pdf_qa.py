import io
import PyPDF2
import numpy as np
import faiss
import google.generativeai as genai
from modules.config import EMBED_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RESULTS


class PDFQAEngine:
    def __init__(self, model):
        self.model    = model
        self.chunks   = []
        self.index    = None
        self.doc_name = ""
        self.history  = []   # continuous chat memory

    # ── ingest ────────────────────────────────────────────────
    def ingest(self, pdf_bytes: bytes, filename: str) -> dict:
        text = self._extract_text(pdf_bytes)
        if not text.strip():
            raise ValueError("No extractable text found in this PDF.")
        self.chunks   = self._chunk(text)
        embeddings    = self._embed_chunks(self.chunks)
        self.index    = self._build_index(embeddings)
        self.doc_name = filename
        self.history  = []   # reset chat on new upload
        return {
            "status":   "indexed",
            "filename": filename,
            "chunks":   len(self.chunks)
        }

    # ── extract text ──────────────────────────────────────────
    def _extract_text(self, pdf_bytes: bytes) -> str:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        pages  = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())
        return "\n\n".join(pages)

    # ── chunking ──────────────────────────────────────────────
    def _chunk(self, text: str) -> list:
        chunks, start = [], 0
        while start < len(text):
            chunks.append(text[start: start + CHUNK_SIZE])
            start += CHUNK_SIZE - CHUNK_OVERLAP
        return chunks

    # ── embed chunks ──────────────────────────────────────────
    def _embed_chunks(self, chunks: list) -> np.ndarray:
        vecs = []
        for chunk in chunks:
            res = genai.embed_content(
                model=EMBED_MODEL,
                content=chunk,
                task_type="RETRIEVAL_DOCUMENT"
            )
            vecs.append(res["embedding"])
        return np.array(vecs, dtype="float32")

    # ── build FAISS index ─────────────────────────────────────
    def _build_index(self, embeddings: np.ndarray):
        idx = faiss.IndexFlatL2(embeddings.shape[1])
        idx.add(embeddings)
        return idx

    # ── answer with continuous memory ─────────────────────────
    def answer(self, question: str) -> str:
        if self.index is None:
            raise ValueError("No document indexed. Upload a PDF first.")

        # embed question
        q_res = genai.embed_content(
            model=EMBED_MODEL,
            content=question,
            task_type="RETRIEVAL_QUERY"
        )
        q_vec = np.array(q_res["embedding"], dtype="float32").reshape(1, -1)

        # retrieve top-k relevant chunks
        _, idxs = self.index.search(q_vec, TOP_K_RESULTS)
        context = "\n\n---\n\n".join(
            self.chunks[i] for i in idxs[0] if i < len(self.chunks)
        )

        # build conversation history string (last 6 turns = 3 Q&A pairs)
        history_str = ""
        if self.history:
            history_str = "\n--- PREVIOUS CONVERSATION ---\n"
            for m in self.history[-6:]:
                role = "User" if m["role"] == "user" else "Assistant"
                history_str += f"{role}: {m['content']}\n"
            history_str += "--- END CONVERSATION ---\n"

        # full prompt with memory + context + anti-hallucination
        prompt = f"""You are an intelligent document Q&A assistant with conversation memory.

STRICT RULES:
1. Answer using the document excerpts provided below.
2. Use conversation history to understand follow-up questions.
3. If the answer is not in the document, say "I couldn't find that in the document."
4. NEVER make up information not present in the document.
5. For follow-up questions like "explain more", "what about X", refer to previous answers.
6. Be detailed, specific, and helpful.
7. If asked to rate or analyze, use ALL information from the document to give a thorough answer.

{history_str}

--- DOCUMENT: {self.doc_name} ---
{context}
--- END DOCUMENT ---

Question: {question}

Answer:"""

        reply = self.model.generate_content(prompt).text.strip()

        # save to continuous chat history
        self.history.append({"role": "user",      "content": question})
        self.history.append({"role": "assistant",  "content": reply})

        # keep only last 20 messages to avoid token overflow
        if len(self.history) > 20:
            self.history = self.history[-20:]

        return reply

    # ── clear history ─────────────────────────────────────────
    def clear_history(self):
        self.history = []