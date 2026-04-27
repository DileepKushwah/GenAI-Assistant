"""
Enhanced ChatBot with:
- Full memory-aware prompting
- Anti-hallucination system prompt
- Auto compression of long conversations
- Per-session Gemini ChatSession
"""

from modules.memory import ConversationMemory


class ChatBot:
    def __init__(self, model, memory: ConversationMemory):
        self.model  = model
        self.memory = memory

    def send(self, message: str, session_id: str = "default") -> str:
        # compress if conversation is getting too long
        self.memory.compress_if_needed(session_id, self.model)

        # build full context-aware prompt
        prompt = self.memory.build_prompt(session_id, message)

        try:
            response = self.model.generate_content(prompt)
            reply    = response.text.strip()
        except Exception as e:
            reply = f"I encountered an error: {str(e)}"

        # save both sides to memory
        self.memory.add(session_id, "user",      message)
        self.memory.add(session_id, "assistant", reply)

        return reply