import google.generativeai as genai
import os

# Read API Key (works for both .env and Streamlit Secrets)

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError(
        " GOOGLE_API_KEY not found. "
        "Add it to your .env (local) or Streamlit Secrets (cloud)."
    )


# Configure Gemini

genai.configure(api_key=API_KEY)

# Use stable free-tier model
model = genai.GenerativeModel("gemini-1.5-flash")

# Ask LLM Function

def ask_llm(prompt: str) -> str:
    """
    Send prompt to Gemini and return response text.
    Safe for Streamlit deployment.
    """
    try:
        response = model.generate_content(prompt)

        # Safety check
        if hasattr(response, "text"):
            return response.text
        else:
            return " No response received from Gemini."

    except Exception as e:
        return f" Gemini Error: {str(e)}"
