import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from utils.llm import ask_llm

def extract_video_id(url):
    if "shorts" in url:
        return url.split("/")[-1]
    elif "v=" in url:
        return url.split("v=")[-1]
    return None

def video_ui():
    st.header("🎥 Video Summarizer")

    url = st.text_input("Enter YouTube URL")

    if st.button("Summarize"):

        video_id = extract_video_id(url)

        if not video_id:
            st.error("Invalid URL")
            return

        try:
            ytt_api = YouTubeTranscriptApi()
            transcript = ytt_api.fetch(video_id).to_raw_data()

            text = " ".join([i["text"] for i in transcript])
            text = text[:3000]

            summary = ask_llm(f"Summarize this video:\n{text}")

            st.write(summary)

        except:
            st.error("Transcript not available")
