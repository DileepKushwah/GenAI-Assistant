import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load local .env if it exists (for local dev)
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL  = "gemini-1.5-flash"
EMBED_MODEL   = "models/gemini-embedding-001"
CHUNK_SIZE    = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 4
MAX_HISTORY   = 10

def init_gemini():
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set. Please set it in your environment or .env file.")
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel(GEMINI_MODEL)
