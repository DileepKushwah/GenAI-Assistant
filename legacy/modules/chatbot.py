import streamlit as st
from utils.llm import ask_llm
from utils.summary_memory import update_summary

import speech_recognition as sr
import pyttsx3
from pypdf import PdfReader
from youtube_transcript_api import YouTubeTranscriptApi

import csv
import datetime
import os


# -------- SAVE CHAT FILE --------
CHAT_FILE = "chat_history.csv"

def save_chat(role, message):

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.exists(CHAT_FILE)

    with open(CHAT_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["time","role","message"])

        writer.writerow([timestamp, role, message])


# -------- VOICE INPUT --------
def listen_voice():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening...")
            audio = r.listen(source, phrase_time_limit=5)
        return r.recognize_google(audio)
    except:
        return ""


# -------- VOICE OUTPUT --------
def speak_text(text):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except:
        pass


# -------- CHATBOT UI --------
def chatbot_ui():

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "summary_memory" not in st.session_state:
        st.session_state.summary_memory = ""

    if "mode" not in st.session_state:
        st.session_state.mode = "chat"

    # -------- SHOW CHAT --------
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # -------- + MENU --------
    with st.popover("➕"):
        if st.button("📄 Document Upload"):
            st.session_state.mode = "doc"

        if st.button("🎥 Video Summarization"):
            st.session_state.mode = "video"

        if st.button("💬 Normal Chat"):
            st.session_state.mode = "chat"

    # -------- DOCUMENT MODE --------
    pdf_text = ""
    if st.session_state.mode == "doc":
        pdf = st.file_uploader("Upload PDF", type="pdf")
        if pdf:
            reader = PdfReader(pdf)
            for page in reader.pages:
                pdf_text += page.extract_text()

    # -------- VIDEO MODE --------
    video_text = ""
    if st.session_state.mode == "video":
        url = st.text_input("Enter YouTube URL")
        if url:
            try:
                video_id = url.split("v=")[-1]
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                video_text = " ".join([i["text"] for i in transcript])
            except:
                st.warning("Transcript not available")

    # -------- MIC BUTTON (ONLY WHEN CLICKED) --------
    voice_text = ""
    if st.button("🎤"):
        voice_text = listen_voice()

    # -------- GPT STYLE ICON OVERLAY --------
    st.markdown("""
    <div class="plus-inside"></div>
    <div class="mic-inside"></div>
    <div class="voice-circle"></div>
    """, unsafe_allow_html=True)

    # -------- INPUT BOX --------
    user_input = st.chat_input("Ask anything")

    if voice_text:
        user_input = voice_text

    # -------- MESSAGE FLOW --------
    if user_input:

        st.session_state.messages.append(
            {"role":"user","content":user_input}
        )

        save_chat("user", user_input)

        with st.chat_message("user"):
            st.write(user_input)

        # ----- PROMPT LOGIC -----
        if st.session_state.mode == "doc":
            prompt = f"""
Answer from document:
{pdf_text}

Question:
{user_input}
"""

        elif st.session_state.mode == "video":
            prompt = f"""
Summarize this video:
{video_text}
"""

        else:
            prompt = f"""
Conversation Summary:
{st.session_state.summary_memory}

User:
{user_input}
"""

        with st.chat_message("assistant"):
            reply = ask_llm(prompt)
            st.write(reply)

        speak_text(reply)

        st.session_state.messages.append(
            {"role":"assistant","content":reply}
        )

        save_chat("assistant", reply)

        # -------- MEMORY UPDATE --------
        if len(st.session_state.messages) % 4 == 0:
            st.session_state.summary_memory = update_summary(
                st.session_state.messages
            )
