"""
Enhanced Memory Module
- Persistent multi-session memory
- Anti-hallucination context injection
- Long conversation sliding window with summary compression
- User profile memory (remembers name, preferences, facts)
"""

from collections import defaultdict
from datetime import datetime

MAX_HISTORY        = 20   # max turns before compression
COMPRESS_TO        = 10   # keep last N turns after compression
MAX_TOKENS_APPROX  = 8000 # rough char limit before compressing


class ConversationMemory:
    def __init__(self):
        # full message history per session
        self._store: dict[str, list] = defaultdict(list)
        # compressed summaries of older turns
        self._summaries: dict[str, list] = defaultdict(list)
        # user profile facts (name, preferences, etc.)
        self._profiles: dict[str, dict] = defaultdict(dict)
        # session metadata
        self._meta: dict[str, dict] = defaultdict(dict)

    # ── add message ───────────────────────────────────────────
    def add(self, session_id: str, role: str, content: str):
        timestamp = datetime.now().strftime("%H:%M")
        self._store[session_id].append({
            "role": role,
            "content": content,
            "time": timestamp
        })
        # extract and store user facts automatically
        if role == "user":
            self._extract_profile(session_id, content)
        # update meta
        self._meta[session_id]["last_active"] = timestamp
        self._meta[session_id]["total_turns"] = len(self._store[session_id])

    # ── extract user facts ────────────────────────────────────
    def _extract_profile(self, session_id: str, text: str):
        t = text.lower()
        profile = self._profiles[session_id]

        # name detection
        for phrase in ["my name is ", "i am ", "i'm ", "call me "]:
            if phrase in t:
                idx = t.find(phrase) + len(phrase)
                name = text[idx:].split()[0].strip(".,!?")
                if len(name) > 1:
                    profile["name"] = name.capitalize()

        # language preference
        if any(w in t for w in ["in hindi", "hindi mein", "हिंदी"]):
            profile["language"] = "Hindi"
        elif any(w in t for w in ["in english", "english me"]):
            profile["language"] = "English"

        # domain/topic interests
        for domain in ["machine learning", "python", "data science", "ai", "coding",
                        "mathematics", "physics", "history", "finance"]:
            if domain in t:
                interests = profile.get("interests", set())
                if isinstance(interests, list):
                    interests = set(interests)
                interests.add(domain)
                profile["interests"] = list(interests)

    # ── get history ───────────────────────────────────────────
    def get_history(self, session_id: str) -> list:
        return self._store.get(session_id, [])

    def get_profile(self, session_id: str) -> dict:
        return self._profiles.get(session_id, {})

    def get_summaries(self, session_id: str) -> list:
        return self._summaries.get(session_id, [])

    # ── build full prompt context ─────────────────────────────
    def build_prompt(self, session_id: str, user_message: str) -> str:
        history   = self._store[session_id]
        summaries = self._summaries[session_id]
        profile   = self._profiles[session_id]

        parts = []

        # 1. System persona + anti-hallucination rules
        parts.append("""You are a helpful, honest, and memory-aware AI assistant.

STRICT RULES TO FOLLOW:
1. NEVER make up facts, statistics, or information you are not sure about.
2. If you don't know something, say "I don't know" or "I'm not sure about that."
3. NEVER contradict what the user told you earlier in this conversation.
4. Remember and use everything the user has shared in this conversation.
5. Keep responses focused, clear, and accurate.
6. If the user asks about something from earlier in the conversation, refer back to it correctly.
7. Do not repeat yourself unnecessarily.
8. Be consistent — your answers must not contradict each other.""")

        # 2. User profile
        if profile:
            parts.append("\n--- USER PROFILE (remembered facts) ---")
            if "name" in profile:
                parts.append(f"User's name: {profile['name']}")
            if "language" in profile:
                parts.append(f"Preferred language: {profile['language']}")
            if "interests" in profile:
                parts.append(f"Interests: {', '.join(profile['interests'])}")
            parts.append("--- END PROFILE ---")

        # 3. Compressed summaries of older conversation
        if summaries:
            parts.append("\n--- SUMMARY OF EARLIER CONVERSATION ---")
            for s in summaries:
                parts.append(s)
            parts.append("--- END SUMMARY ---")

        # 4. Recent conversation history
        if history:
            parts.append("\n--- RECENT CONVERSATION ---")
            for m in history:
                role_label = "User" if m["role"] == "user" else "Assistant"
                parts.append(f"[{m['time']}] {role_label}: {m['content']}")
            parts.append("--- END CONVERSATION ---")

        # 5. Current message
        parts.append(f"\nUser: {user_message}")
        parts.append("Assistant:")

        return "\n".join(parts)

    # ── compress old turns to free context ───────────────────
    def compress_if_needed(self, session_id: str, model) -> bool:
        history = self._store[session_id]
        total_chars = sum(len(m["content"]) for m in history)

        if len(history) < MAX_HISTORY and total_chars < MAX_TOKENS_APPROX:
            return False

        # take the oldest half to compress
        to_compress = history[:-COMPRESS_TO]
        keep        = history[-COMPRESS_TO:]

        if not to_compress:
            return False

        # build a mini transcript to summarize
        transcript = "\n".join(
            f"{'User' if m['role']=='user' else 'Assistant'}: {m['content']}"
            for m in to_compress
        )

        prompt = f"""Summarize this conversation segment in 3-5 concise bullet points.
Preserve: key facts the user shared, important decisions made, topics discussed.
Do NOT add any information not present in the transcript.

Transcript:
{transcript}

Summary (bullet points):"""

        try:
            response = model.generate_content(prompt)
            summary  = response.text.strip()
            self._summaries[session_id].append(summary)
            # keep only recent turns
            self._store[session_id] = keep
            return True
        except Exception:
            # if compression fails, just trim
            self._store[session_id] = keep
            return False

    # ── clear ─────────────────────────────────────────────────
    def clear(self, session_id: str):
        self._store[session_id]    = []
        self._summaries[session_id]= []
        self._profiles[session_id] = {}
        self._meta[session_id]     = {}

    # ── stats ─────────────────────────────────────────────────
    def stats(self, session_id: str) -> dict:
        history = self._store[session_id]
        return {
            "total_messages": self._meta[session_id].get("total_turns", 0),
            "active_messages": len(history),
            "compressions": len(self._summaries[session_id]),
            "profile": self._profiles[session_id],
            "last_active": self._meta[session_id].get("last_active", "—"),
        }