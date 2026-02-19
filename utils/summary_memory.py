from utils.llm import ask_llm

def update_summary(history):

    # combine history text
    text = "\n".join([f"{m['role']}: {m['content']}" for m in history])

    summary = ask_llm(
        f"""
Summarize this conversation briefly.
Keep only important context.
Max 100 words:

{text}
"""
    )

    return summary
