def route_task(user_input: str):
    text = user_input.lower()

    if "video" in text or "youtube" in text:
        return "video"

    elif "pdf" in text or "document" in text:
        return "rag"

    elif "image" in text or "generate" in text or "draw" in text:
        return "image"

    else:
        return "chat"
