"""
Voice input module.
Uses SpeechRecognition library to capture microphone input
and convert it to text that feeds into the chatbot.
"""

import streamlit as st

# Try importing speech recognition; gracefully degrade if unavailable
try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False


def transcribe_from_microphone(timeout: int = 5, phrase_limit: int = 15) -> str:
    """
    Records from the default microphone and returns transcribed text.
    Returns an error string if something goes wrong.
    """
    if not SPEECH_AVAILABLE:
        return "[Voice input unavailable: install pyaudio and SpeechRecognition]"

    r = sr.Recognizer()
    r.energy_threshold = 300
    r.dynamic_energy_threshold = True

    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)

        text = r.recognize_google(audio)
        return text

    except sr.WaitTimeoutError:
        return "[No speech detected — please try again]"
    except sr.UnknownValueError:
        return "[Could not understand audio — please speak clearly]"
    except sr.RequestError as e:
        return f"[Speech API error: {e}]"
    except OSError:
        return "[Microphone not found — check your audio device]"


# ── Streamlit voice widget ─────────────────────────────────────
def voice_input_widget() -> str | None:
    """
    Renders a mic button. Returns transcribed text or None.
    Call this inside your chatbot UI and use the returned text
    as the user's message.
    """
    if not SPEECH_AVAILABLE:
        st.caption("🎙️ Voice input requires `pyaudio` — install it to enable.")
        return None

    col1, col2 = st.columns([1, 4])
    with col1:
        mic_btn = st.button("🎙️ Speak", help="Click and speak your question")
    with col2:
        st.caption("Listens for up to 15 seconds")

    if mic_btn:
        with st.spinner("🎙️ Listening... speak now"):
            text = transcribe_from_microphone()

        if text.startswith("["):
            st.warning(text)
            return None
        else:
            st.success(f"Heard: *{text}*")
            return text

    return None
